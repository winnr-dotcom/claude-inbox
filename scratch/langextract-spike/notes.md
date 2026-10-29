# LangExtract spike notes (issue #18)

Source: README at github.com/google/langextract (read via fetch). Demo in `demo.py` is **not yet run**.

## What it does well
- Few-shot extraction, no fine-tuning: prompt + 1–few examples -> typed extractions.
- Every extraction carries a `char_interval` into the source (grounding); `None` = not found, filter those out. Good for audit/"show me where".
- Long text: chunking (`max_char_buffer`), `extraction_passes` for recall, `max_workers` for parallelism.
- Providers: Gemini, OpenAI, Ollama (local), plugin system for others. Self-contained HTML review view via `lx.visualize`.
- Apache-2.0.

## Limits
- Text only. README says nothing on PDFs. Needs a pre-step: HTML -> trafilatura/readability; text PDFs -> pdfplumber/pypdf; scans -> OCR (Tesseract with `nor` language pack, or a cloud OCR). Tables/layout get flattened, which hurts invoices.
- Quality depends on model + examples; small local models (gemma2:2b) are weak, especially on Norwegian. Examples must be verbatim and in order or alignment warns.
- Ollama: no `output_schema` (schema constraints), so output is less reliable.
- Model may echo few-shot example text.
- Not an officially supported Google product; Gemini model IDs get retired, so pin and review.
- Cost: Gemini free tier is rate-limited; paid tier / batch APIs for volume. Cost is per input token (prompt + examples repeated per chunk, times passes). Check current Google pricing before quoting numbers; I did not measure any.

## Recommendation (preliminary, untested)
- Worth a small, optional extractor inside a Fundarem document connector: it is thin, license-friendly, and grounding is a real differentiator for trust.
- Do not treat it as the document pipeline. The hard part is text/OCR/layout, which it does not solve.
- Alternative: plain structured output from Claude/Gemini with a JSON schema, plus asking for a verbatim quote and verifying it with a string search. This gives most of the grounding with no extra dependency. LangExtract's edge is chunking, multi-pass, and the review UI.
- Next step before deciding: run `demo.py` on 3 real Norwegian grant pages with Gemini free tier, and compare against the schema+quote approach.
