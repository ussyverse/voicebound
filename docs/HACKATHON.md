# Hackathon compliance checklist (not a certification)

Checked 2026-09-16 UTC / September 15 Eastern against official pages:

- Event and registration: https://lablab.ai/ai-hackathons/assemblyai-voice-agent-hackathon
- General rules: https://lablab.ai/hackathon-rules
- General participation guide: https://lablab.ai/guide
- API reference: https://www.assemblyai.com/docs/pre-recorded-audio/api-reference/transcripts/submit

## Verified event requirements and design response

The event runs September 1–30, 2026, online. Registration stays open throughout the build window. Deadline displayed is September 30 at 08:00 PDT. Every participant builds on AssemblyAI. The advertised $10,000 pool is $5,000 cash plus $5,000 credits, not all cash.

Voicebound uses AssemblyAI as the player speech-to-text provider. OmniVoice is speech output and Luna through a tool-free Hermes gateway is dialogue inference. They do not replace the sponsor integration. Typed play is an accessibility/development path; it alone does not demonstrate the required AssemblyAI use. A real AssemblyAI transcription must be verified before describing the entry as voice-complete.

New standalone original story/code started during the listed build period. No private project source, personal recordings, profile libraries or credentials may be published. Synthetic game voices only. Document all AI assistance; the human registers and submits, not an invented AI contestant.

## General submission requirements still to complete

- [ ] Human registration / team enrollment (solo entrants also need a team per guide).
- [ ] Confirm personal eligibility and event-specific terms during enrollment.
- [ ] Confirm organizer permission for our AI-assisted development workflow and external Luna/OmniVoice tools if not explicit in event-specific terms. An AI-themed event is not blanket permission for unauthorized automation.
- [ ] End-to-end real AssemblyAI microphone -> transcript -> confirmed player action -> Luna dialogue -> OmniVoice audio demonstration.
- [ ] Public GitHub repository with original code, licensing and setup instructions.
- [ ] Interactive application URL. General rules name Streamlit, Replit or Vercel. Target Replit for the FastAPI app; do not count a loopback/private test URL as satisfying this. Production needs private authenticated connectivity to inference/voice services; never expose the broad OmniVoice Studio API.
- [ ] 16:9 PNG/JPG cover image.
- [ ] MP4 presentation and PDF pitch slides.
- [ ] Title, short/long descriptions within actual form limits and appropriate technology/category tags.
- [ ] Privacy notice/consent for recordings and third-party processing; review retention/deletion with AssemblyAI and OmniVoice operators.
- [ ] Review sponsor terms, open-source/model licenses, public deployment security and spending limits before public launch.

Judging categories listed: presentation, business value, application of technology and originality. Position the prototype as an accessible, replayable voice-first narrative interface, not simply a chat wrapper. Maintain honest provider/test evidence. Do not fake sponsor usage, claim unsupported model capabilities or manipulate votes.

## Unresolved rules

The public event summary and general rules reviewed do not explicitly settle age/country eligibility, maximum team size, exact AI coding-assistant permissions, extra-model restrictions, pre-existing component allowances, or event-specific judging weights. Confirm at registration or with organizers. No organizer communication, registration or submission has been performed by the assistant. This repository is work in progress, not a completed/approved entry.

## Current AssemblyAI model parameter

On the check date, the API reference enum and model documentation list `universal-3-5-pro` and `universal-2` as supported `speech_models`, while some sample JSON still shows older `universal-3-pro`. Follow the enum/model documentation; record the model returned by the service and do not claim a live transcription until one succeeds.
