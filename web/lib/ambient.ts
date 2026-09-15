// Original synthesized observatory hum; no samples or third-party audio assets.
export class ObservatoryAudio {
  private context: AudioContext | null = null;
  private master: GainNode | null = null;
  private sources: OscillatorNode[] = [];
  private enabled = false;
  private request = 0;

  async setEnabled(enabled: boolean) {
    const request = ++this.request;
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

  private fade(audible: boolean) {
    if (!this.context || !this.master) return;
    const time = this.context.currentTime;
    this.master.gain.cancelScheduledValues(time);
    this.master.gain.setTargetAtTime(audible ? 1 : 0, time, 0.18);
  }

  visibilityChanged = () => this.fade(this.enabled && !document.hidden);

  dispose() {
    this.request++;
    this.sources.forEach(source => source.stop());
    this.sources = [];
    void this.context?.close();
    this.context = null;
    this.master = null;
  }
}
