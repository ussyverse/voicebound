# Voicebound: The Last Broadcast

A voice-first mystery in a stormbound radio station. Search three locations, collect evidence, question three fictional suspects, and decide who hid a recording. A compact original hackathon work in progress, not a finished or organizer-approved entry.

**AssemblyAI listens → you confirm the transcript → Luna responds → OmniVoice speaks.**

## Current state

- Playable browser investigation with an authoritative authored mystery, evidence board and accusation outcome.
- Real Luna (`gpt-5.6-luna`, high reasoning) through a tool-free Hermes gateway; no direct provider fallback.
- Real OmniVoice Studio WAV generation, explicit playback and exact captions. Character IDs persist synthetic instruction/seed recipes in saved cases.
- AssemblyAI upload/transcript/poll adapter and consent-based microphone UI. **Not live-verified: an AssemblyAI API key is needed.** Offline adapter tests are not proof of sponsor usage.
- SQLite saves and transcript, revision conflict checks, browser session isolation and bounded provider-call quotas.
- **Local/private prototype only**, not yet an internet-hardened public judging deployment.

## Run

Requires Python 3.11+, uv, access to your own configured providers.

```sh
uv sync
cp .env.example .env
# Edit .env with your own server-side credentials and endpoints.
uv run uvicorn app:app --host 127.0.0.1 --port 8901
```

Open http://127.0.0.1:8901. Inspecting locations and making an accusation work without a model. Asking a character requires Luna; speech playback requires OmniVoice; microphone transcription requires AssemblyAI. Missing/unavailable providers return explicit errors, never fabricated results.

The default hostname allowlist is `localhost,127.0.0.1`. Do not bind to the public internet without authentication, TLS, carefully configured allowed hosts, durable global spending controls and a review of upload/resource limits. Quotas are an aid, not access control. Use one Uvicorn worker: request serialization is in-process.

## How to play

Start a case. Search the console, engineering bench and tape archive. Select a suspect, type a question or record a short one. Recording stays in the browser until you consent and click **Transcribe with AssemblyAI**. Review/edit the resulting text, then click **Ask selected suspect**. Speech recognition never silently advances the case. Click **Hear** on a character line to generate audio; Stop playback controls the current browser audio, not remote synthesis already in progress. Collect all clues before accusing someone. Character testimony is not authoritative evidence.

The story is an original fixed case, not an infinitely generated mystery. The open-source server necessarily contains the solution; normal browser game responses omit undiscovered clues. Avoid reading `story.py` if you want to play unspoiled.

## Providers

### AssemblyAI (required sponsor integration)

Set `ASSEMBLYAI_API_KEY`. The backend sends recorded bytes to `https://api.assemblyai.com/v2/upload`, submits a transcription using `speech_models: ["universal-3-5-pro", "universal-2"]`, and polls with a finite budget. The current documented enum, not older sample JSON, informed model selection. Successful responses include the transcript ID and reported model. These are processed by AssemblyAI, subject to its terms and retention. No browser Web Speech fallback bypasses the sponsor. Confirm current pricing/credits before use.

The browser records up to 30 seconds; the server enforces a 5 MiB file limit, not a server-validated duration limit. No uploaded recording is deliberately saved by this application, but framework temporary spooling and provider-side storage can occur. A timed-out remote transcript job may still complete and incur cost.

### Luna through Hermes

Set `LUNA_GATEWAY_URL`, `LUNA_GATEWAY_KEY`, and optionally `LUNA_MODEL` (default `gpt-5.6-luna`). The endpoint must support Hermes `/v1/chat/completions`, `provider: openai-codex` and `model_options.reasoning_effort: high`. Use a **dedicated tool-free, personal-memory-free game gateway**. Do not point untrusted player text at a general assistant gateway with shell/browser tools or personal memories. This repository does not bundle provider credentials or copy them automatically.

Luna receives only the selected character's public brief, discovered evidence and recent visible dialogue. It cannot mutate game state. JSON response shape and length are checked, but semantic hallucinations remain possible: testimony is visibly labeled as unverified. No hidden chain-of-thought is collected. Dialogue records requested/reported model identifiers, not secrets.

### OmniVoice Studio

Set the operator-controlled `OMNIVOICE_BASE_URL` to a privately reachable Studio service. The backend uses multipart `POST /generate` with short text, synthetic `instruct`, persistent seed/language and basic generation settings. PCM RIFF WAV responses are checked; audio is at most 8 MiB / 120 seconds, with a 64 MiB local cache. Only a server-stored character line owned by the current session can request speech. Requests cannot supply arbitrary text, URLs or profile IDs.

No personal profile library is read and no real person's voice is cloned. A fixed recipe/seed does **not** guarantee identical timbre across different utterances. This Studio endpoint returns a completed utterance, not token-real-time synthesis; latency may be substantial. Studio may keep its own generation history. Do not expose its broad administration/profile API publicly. The installed model's own license and terms remain the operator's responsibility; this repository's MIT license covers our code, not external models.

## Verification

```sh
uv run pytest -q
node --check static/app.js
# With configured providers and the local server running (real calls consume quota):
uv run python live_smoke.py
# Optional browser QA: install Playwright in an environment with Chromium first.
python browser_qa.py
```

Initial run: **11 offline tests passed**. Browser QA passed new case, all three clues, reload persistence, correct accusation and mobile layout without horizontal overflow or JS exceptions. Tests explicitly mock providers; the browser QA exercises real rules, not provider calls.

Separate real-provider smoke returned Luna's requested and reported model `gpt-5.6-luna`, generated a 447,404-byte 24 kHz PCM WAV lasting 9.32 seconds through OmniVoice, then completed and reloaded a solved case. That sample's Luna call took 5.97 seconds and synthesis 34.92 seconds. These are one observed run, not performance guarantees. **No live AssemblyAI result is claimed.** Local evidence is deliberately excluded from git under `.runtime/`.

## Hackathon / next gates

Register: https://lablab.ai/ai-hackathons/assemblyai-voice-agent-hackathon

The listed deadline is September 30, 2026 at 08:00 PDT. Registration remains open during the build window. See [the compliance checklist](docs/HACKATHON.md) for exact sources and unresolved conditions. We must still verify personal/event-specific eligibility and any ambiguous additional-AI-tool rules, complete real AssemblyAI integration testing, deploy an interactive demo on an allowed platform (target: Replit), and prepare a 16:9 cover, MP4 demonstration and PDF pitch. A localhost demo does not satisfy the public application URL requirement.

The human entrant registers/submits and owns their decisions. Development used AI assistance; no claim is made that the AI is a human team member. This fresh standalone code does not include private prior projects. No automatic registration, submission, billing setup or vote automation is included.

## Privacy and storage

`.env` and `.runtime/` are ignored. Treat the browser cookie as a case capability; the SQLite database contains dialogue and evidence and must be protected. Cases currently have no automatic deletion UI/retention job; stop the app and remove your runtime directory to clear local cases/audio. This does not delete data held by providers. Review that limitation before public deployment. Audio cache, provider requests and API keys stay server-side; neither model responses nor user input are inserted as HTML.

## Walkable Three.js station

The interface now includes a locally bundled Three.js 0.170.0 scene. WASD/arrows walk, dragging looks around, and E interacts with nearby desks or people. Touch buttons support movement, turning and interaction. Desks reveal existing engine clues; approaching a character selects the existing Luna/voice conversation panel. Solid desks, people and perimeter walls block movement. Escape releases controls. The complete text interface remains available without WebGL. These are original procedural placeholder assets, not final art. No CDN is required at runtime. Third-party Three.js MIT license: `static/vendor/THREE-LICENSE.txt`.

Verified in Chromium: WebGL rendering, walking to Inez and selecting dialogue, walking to the archive and discovering its actual clue, mobile width and no JavaScript exceptions.

## Immersive scene mode

The default presentation fills the browser window. Opening story, proximity prompt, casebook, witness conversations, editable questions and accusation confirmation are drawn as Three.js canvas-texture UI inside the rendered scene. WASD/arrows move; drag looks; E interacts; J opens the casebook; Escape returns to exploration. Click the question area and type, then Enter to ask Luna. On-screen arrows provide short touch movement steps. Text view retains the accessible page interface. This is an atmosphere/interface upgrade to the existing fixed mystery, not a new procedural campaign.
