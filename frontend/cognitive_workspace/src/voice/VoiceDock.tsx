export function VoiceDock({ onPtt }: { onPtt: () => void }) {
  return (
    <section className="voice-dock">
      <button onMouseDown={onPtt}>Push to talk</button>
      <span className="subtitles">Live subtitles overlay</span>
    </section>
  );
}
