type Handler = (payload: unknown) => void;

export class StreamSynchronizer {
  private ws: WebSocket | null = null;
  private handlers = new Map<string, Set<Handler>>();

  connect(url: string) {
    this.ws = new WebSocket(url);
    this.ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data as string) as { channel?: string; payload?: unknown };
        const ch = msg.channel ?? "runtime";
        this.handlers.get(ch)?.forEach((h) => h(msg.payload));
      } catch {
        /* ignore malformed frames */
      }
    };
  }

  subscribe(channel: string, handler: Handler) {
    if (!this.handlers.has(channel)) this.handlers.set(channel, new Set());
    this.handlers.get(channel)!.add(handler);
    return () => this.handlers.get(channel)?.delete(handler);
  }

  throttleFps(cap: number): number {
    return Math.max(1000 / cap, 16);
  }
}

export const streamSync = new StreamSynchronizer();
