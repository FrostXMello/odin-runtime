type Props = { transcript: string; pushToTalk: boolean; onPtt: () => void };

export function VoiceConsole({ transcript, pushToTalk, onPtt }: Props) {
  return (
    <section className="voice-console">
      <button className={pushToTalk ? "ptt active" : "ptt"} onMouseDown={onPtt}>
        Push to talk
      </button>
      <p className="subtitles">{transcript || "…"}</p>
    </section>
  );
}
