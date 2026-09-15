// Original synthesized hum, instrument detents and camera sweeps. No downloaded samples.
export class ObservatoryAudio {
  private context: AudioContext | null = null;
  private master: GainNode | null = null;
  private sources: OscillatorNode[] = [];
  private enabled = false;
  private request = 0;
  private voices = new Map<OscillatorNode, GainNode>();
  private lastClick = -Infinity;

  async setEnabled(enabled: boolean) {
    const request = ++this.request;
    if (!enabled) {
      this.enabled = false;
      this.stopVoices();
      this.fade(false);
    }
    if (enabled && !this.context) {
      this.context = new AudioContext();
      this.master = this.context.createGain();
      this.master.gain.value = 0;
      this.master.connect(this.context.destination);
      // Gentle beating between nearby tones, with a quieter upper harmonic.
      for (const [frequency, volume] of [[110, 0.022], [110.18, 0.015], [220, 0.01], [330, 0.004]]) {
        const oscillator = this.context.createOscillator();
        const level = this.context.createGain();
        oscillator.type = 'sine';
        oscillator.frequency.value = frequency;
        level.gain.value = volume;
        oscillator.connect(level).connect(this.master);
        oscillator.start();
        this.sources.push(oscillator);
      }
    }
    if (enabled && this.context) await this.context.resume();
    if (request !== this.request) return this.enabled;
    this.enabled = enabled && this.context?.state === 'running';
    this.fade(this.enabled && !document.hidden);
    return this.enabled;
  }

  // Five restrained pitches, ordered exactly as the instruments in the scroll journey.
  click(index = 0) {
    if (!this.audible()) return;
    const now = this.context!.currentTime;
    if (now - this.lastClick < .075) return;
    this.lastClick = now;
    const pitch = [660, 520, 440, 780, 880][index] ?? 660;
    this.tone(pitch, pitch * .64, .12, .032);
  }

  transition(direction: 'in' | 'out') {
    if (!this.audible()) return;
    this.stopVoices();
    const incoming = direction === 'in';
    this.tone(incoming ? 165 : 330, incoming ? 330 : 165, .78, .025);
    this.tone(incoming ? 247 : 494, incoming ? 494 : 247, .66, .009);
  }

  private audible() {
    return this.enabled && !document.hidden && this.context?.state === 'running';
  }

  private tone(from: number, to: number, duration: number, volume: number) {
    if (!this.context || !this.master || this.voices.size >= 6) return;
    const now = this.context.currentTime;
    const oscillator = this.context.createOscillator();
    const level = this.context.createGain();
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(from, now);
    oscillator.frequency.exponentialRampToValueAtTime(to, now + duration);
    level.gain.setValueAtTime(0, now);
    level.gain.linearRampToValueAtTime(volume, now + .012);
    level.gain.exponentialRampToValueAtTime(.0001, now + duration);
    oscillator.connect(level).connect(this.master);
    this.voices.set(oscillator, level);
    oscillator.onended = () => {
      oscillator.disconnect();
      level.disconnect();
      this.voices.delete(oscillator);
    };
    oscillator.start(now);
    oscillator.stop(now + duration + .02);
  }

  private stopVoices() {
    for (const [source, level] of this.voices) {
      source.onended = null;
      source.stop();
      source.disconnect();
      level.disconnect();
    }
    this.voices.clear();
  }

  private fade(audible: boolean) {
    if (!this.context || !this.master) return;
    const time = this.context.currentTime;
    this.master.gain.cancelScheduledValues(time);
    this.master.gain.setTargetAtTime(audible ? 1 : 0, time, 0.18);
  }

  visibilityChanged = () => {
    if (document.hidden) this.stopVoices();
    this.fade(this.enabled && !document.hidden);
  };

  dispose() {
    this.request++;
    this.enabled = false;
    this.stopVoices();
    this.sources.forEach(source => { source.stop(); source.disconnect(); });
    this.sources = [];
    void this.context?.close();
    this.context = null;
    this.master = null;
  }
}
