import { Entry, Log, Logging } from '@google-cloud/logging';

export enum Severity {
  Info = 1,
  Warning = 2,
  Error = 3,
}

class BatchLogger {
  private static FLUSH_DELAY = 30000; // ms
  private static ENTRIES_LIMIT = 100;

  private entries: Entry[] = [];
  private flushTimer: NodeJS.Timer;

  public constructor(private log: Log, private severity: Severity) {}

  public buffer(message: string): void {
    switch (this.severity) {
      case Severity.Info:
        console.info(message);
        break;
      case Severity.Warning:
        console.warn(message);
        break;
      case Severity.Error:
        console.error(message);
        break;
      default:
        console.log(message);
    }

    let entry = this.log.entry(message);
    this.entries.push(entry);
    if (this.entries.length < BatchLogger.ENTRIES_LIMIT) {
      if (!this.flushTimer) {
        this.flushTimer = setTimeout(this.flush, BatchLogger.FLUSH_DELAY);
      }
    } else {
      if (this.flushTimer) {
        clearTimeout(this.flushTimer);
      }
      this.flush();
    }
  }

  private flush = (async (): Promise<void> => {
    try {
      switch (this.severity) {
        case Severity.Info:
          await this.log.info(this.entries);
          break;
        case Severity.Warning:
          await this.log.warning(this.entries);
          break;
        case Severity.Error:
          await this.log.error(this.entries);
          break;
        default:
          await this.log.info(this.entries);
      }
    } catch(e) {
      // Do nothing
    }

    this.entries = [];
    this.flushTimer = undefined;
  });
}

class Logger {
  private severityToBatchLoggers = new Map<string, BatchLogger>();
  private logging: Logging;
  private log: Log;

  public constructor() {
    this.logging = new Logging();
    this.log = this.logging.log('Backend');
  }

  public info(message: string) {
    let batchLogger = this.getBatchLogger(Severity.Info);
    batchLogger.buffer(message);
  }

  private getBatchLogger(severity: Severity): BatchLogger {
    let batchLogger = this.severityToBatchLoggers.get(Severity[severity]);
    if (!batchLogger) {
      batchLogger = new BatchLogger(this.log, severity);
      this.severityToBatchLoggers.set(Severity[severity], batchLogger);
    }
    return batchLogger;
  }

  public warning(message: string) {
    let batchLogger = this.getBatchLogger(Severity.Warning);
    batchLogger.buffer(message);
  }

  public error(message: string) {
    let batchLogger = this.getBatchLogger(Severity.Error);
    batchLogger.buffer(message);
  }
}

export let LOGGER = new Logger();
