"""Throwaway LangExtract spike: pull grant-call fields out of Norwegian text.

Run (free options only, no paid keys):
  pip install langextract
  # Option A: local model
  ollama pull gemma2:2b && python demo.py ollama
  # Option B: Gemini free tier (key from aistudio.google.com, export it, never commit it)
  LANGEXTRACT_API_KEY=... python demo.py gemini

NOT RUN YET: written in a CI sandbox with no pip/Ollama/key access.
"""
import sys
import textwrap

import langextract as lx

PROMPT = textwrap.dedent("""\
    Extract grant-call facts in order of appearance, using exact text from the source.
    Classes: organisation (the funder), amount (funding sum or range),
    deadline (application date), eligibility (who may apply).
    Do not paraphrase. Do not invent values.""")

EXAMPLES = [
    lx.data.ExampleData(
        text="Stiftelsen Nordlys deler ut inntil 200 000 kroner til lokale lag. "
             "Søknadsfrist er 1. mars 2025. Kun frivillige organisasjoner kan søke.",
        extractions=[
            lx.data.Extraction("organisation", "Stiftelsen Nordlys"),
            lx.data.Extraction("amount", "inntil 200 000 kroner"),
            lx.data.Extraction("deadline", "1. mars 2025"),
            lx.data.Extraction("eligibility", "Kun frivillige organisasjoner kan søke"),
        ],
    )
]

# Synthetic sample text (not copied from a real call). Swap in real page text
# (see notes.md on getting text out of HTML/PDF) to test properly.
SAMPLES = {
    "grant_call": (
        "Innovasjon Norge åpner ny utlysning for grønn omstilling i små og mellomstore "
        "bedrifter. Det kan søkes om tilskudd på mellom 100 000 og 1 500 000 kroner. "
        "Søknadsfristen er 15. september 2026 kl. 12:00. Støtteberettigede er norskregistrerte "
        "SMB-er med under 100 ansatte som har drevet virksomhet i minst to år."
    ),
    "invoice": (
        "FAKTURA nr 20931 fra Fjordtech AS, org.nr 912 345 678. Fakturadato 3. oktober 2026. "
        "Forfallsdato 17. oktober 2026. Totalt å betale: kr 48 750,00 inkl. mva."
    ),
}


def main(backend: str) -> None:
    kwargs = (
        dict(model_id="gemma2:2b", model_url="http://localhost:11434",
             fence_output=False, use_schema_constraints=False)
        if backend == "ollama"
        else dict(model_id="gemini-3.5-flash")  # key read from LANGEXTRACT_API_KEY
    )
    for name, text in SAMPLES.items():
        result = lx.extract(text_or_documents=text, prompt_description=PROMPT,
                            examples=EXAMPLES, **kwargs)
        print(f"== {name}")
        for e in result.extractions:
            grounded = e.char_interval is not None  # None => not found in source
            print(f"  {e.extraction_class:13} {e.extraction_text!r} grounded={grounded}")
        lx.io.save_annotated_documents([result], output_name=f"{name}.jsonl", output_dir=".")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ollama")
