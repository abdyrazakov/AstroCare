# v0.5 demo script

Use `LLAMA_KEEP_ALIVE=10m` when running Ollama-backed demonstrations. Start the brain with `python -m astro_brain.dashboard --port 8766 --ws-port 8787`, start the AstroCare frontend with `NEXT_PUBLIC_BRAIN_WS_URL=ws://localhost:8787 npm run dev`, and feed Astralis with its interpreter and `PYTHONPATH=src`.

The three stories are: a quiet day with `MISSED_ARED` and no daily log; a solar particle event that raises radiation and cancels exercise when the red state is reached; and `HYPERCAPNIC_CABIN`, which exposes CO₂ flags, scrubber resources, plans, body zones, and a ground-medical recommendation through `/ask`.
