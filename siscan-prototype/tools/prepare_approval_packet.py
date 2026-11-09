"""Prepare a pending-only source-reference proposal for project-owner review."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from tools.stage_db3k import digest


def prepare_packet(review, evidence):
    review, evidence = Path(review).resolve(strict=True), Path(evidence).resolve(strict=True)
    review_hash, evidence_hash = digest(review), digest(evidence)
    report = json.loads(evidence.read_text(encoding="utf-8"))
    with closing(sqlite3.connect(review.as_uri()+"?mode=ro", uri=True)) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        source = db.execute("SELECT file_name,sha256,read_at FROM source LIMIT 1").fetchone()
        rows = db.execute("SELECT * FROM candidates ORDER BY source_table,external_id").fetchall()
    if not source or report.get("source", {}).get("sha256") != source["sha256"] or report.get("review_sha256") != review_hash or report.get("status") != "evidence_only_not_approved":
        raise ValueError("As evidências não correspondem à amostra e à fonte.")
    matches = {row["candidate_id"]: row for row in report.get("candidates", [])}
    if len(matches) != len(rows) or report.get("literal_records_verified") != len(rows):
        raise ValueError("A conferência literal não cobre toda a amostra.")
    candidates = []
    for row in rows:
        match = matches.get(row["candidate_id"])
        if not match or match.get("literal_source_check") != "matched" or match.get("source_table") != row["source_table"] or match.get("external_id") != row["external_id"]:
            raise ValueError("Candidato sem conferência literal correspondente.")
        candidates.append({"candidate_id": row["candidate_id"], "source_table": row["source_table"],
                           "external_id": row["external_id"], "source_name": row["source_name"],
                           "raw_codes": json.loads(row["raw_codes_json"]), "domain_evidence": match["domains"],
                           "proposed_entity_kind": "source_reference", "decision": "pending", "approved_fields": [],
                           "pending": ["Aprovação explícita do responsável", "Mapeamento semântico modelo/configuração/unidade", "Validação de atributos técnicos e unidades antes de qualquer uso desses atributos"]})
    if review_hash != digest(review) or evidence_hash != digest(evidence):
        raise RuntimeError("Os arquivos mudaram durante a preparação.")
    batch_id = hashlib.sha256(json.dumps([source["sha256"], sorted(matches)], sort_keys=True).encode()).hexdigest()[:16]
    return {"batch_id": "DB3K-"+batch_id, "status": "awaiting_project_owner_review",
            "generated_at": datetime.now(timezone.utc).isoformat(), "source": dict(source),
            "review_sha256": review_hash, "evidence_sha256": evidence_hash,
            "scope": "literal_source_identification_only", "permits_allocation": False,
            "candidates": candidates}


def as_markdown(packet):
    def safe(value):
        return str(value if value is not None else "Ausente").replace("|", "\\|").replace("\n", " ").replace("\r", " ")
    lines = ["# Proposta de referências DB3K para decisão do responsável", "",
             f"Lote: `{packet['batch_id']}`. Situação: **aguardando revisão e aprovação explícita**.", "",
             "A conferência verifica que ID, nome e códigos foram copiados fielmente. Não comprova significado de campos, capacidade operacional ou classificação como modelo, configuração ou unidade individual.", "",
             "Proposta: registrar somente a identificação de referência da fonte (nome literal, tabela, ID externo e hash), sem atributos técnicos. Uma referência de fonte não é uma unidade individual e não poderá ser alocada a um partido. Nenhum campo está aprovado neste pacote.", "",
             f"Fonte: `{packet['source']['file_name']}`. SHA-256: `{packet['source']['sha256']}`.", "",
             "| Tabela | ID externo | Nome literal | Identificador do candidato | Decisão |",
             "|---|---|---|---|---|"]
    for row in packet["candidates"]:
        lines.append(f"| {safe(row['source_table'])} | {safe(row['external_id'])} | {safe(row['source_name'])} | {safe(row['candidate_id'])} | Pendente |")
    lines += ["", "O responsável pode aprovar o escopo de identificação para os candidatos indicados, rejeitar registros ou solicitar ajustes. A aprovação não será presumida a partir da geração/consulta deste pacote. Promoção técnica e alocação não são executadas por esta ferramenta.", "",
              "As descrições literais e pendências por registro constam no JSON do mesmo lote. Vínculos nominais sem FK permanecem explicitamente não confirmados."]
    return "\n".join(lines)+"\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera proposta pendente de referências DB3K; não aprova nem promove dados.")
    parser.add_argument("review", type=Path)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("output", type=Path, help="Novo arquivo JSON; um Markdown do mesmo nome também será criado")
    args = parser.parse_args()
    markdown = args.output.with_suffix(".md")
    if args.output.suffix.lower() != ".json" or args.output.exists() or markdown.exists():
        raise ValueError("Informe um novo destino .json, sem JSON/Markdown existentes.")
    packet = prepare_packet(args.review, args.evidence)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(packet, stream, ensure_ascii=False, indent=2)
    with markdown.open("x", encoding="utf-8") as stream:
        stream.write(as_markdown(packet))
    print(f"{packet['batch_id']}: {len(packet['candidates'])} candidatos; todas as decisões pendentes")
