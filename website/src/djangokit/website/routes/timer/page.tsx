import { useEffect, useRef, useState } from "react";

import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import ProgressBar from "react-bootstrap/ProgressBar";

import { FaPause, FaPlay, FaStop } from "react-icons/fa";

import IconButton from "../../components/IconButton";

const TICK_MS = 50;
const DEFAULT_SECONDS = ENV === "development" ? 5 : 0;

export default function Page() {
  // User input
  const [hours, setHours] = useState(0);
  const [minutes, setMinutes] = useState(0);
  const [seconds, setSeconds] = useState(DEFAULT_SECONDS);

  const [startMs, setStartMs] = useState<number>();
  const [endMs, setEndMs] = useState<number>();
  const [countdown, setCountdown] = useState("");
  const [started, setStarted] = useState(false);
  const [running, setRunning] = useState(false);
  const [pausedAt, setPausedAt] = useState<number>();

  // NOTE: This is only needed in order to force a rerender of the
  //       progress bar on every tick so that it advances smoothly.
  const [numTicks, setNumTicks] = useState<number>(0);

  const [message, setMessage] = useState<string>();

  useInterval(
    () => {
      if (typeof endMs !== "number") {
        throw new Error(`Expected endMs to be a number: ${endMs}`);
      }
      const nowMs = getNowMs();
      setNumTicks(numTicks + 1);
      if (nowMs < endMs) {
        setCountdown(getCountdown(nowMs, endMs));
      } else {
        setCountdown("0");
        done();
      }
    },
    TICK_MS,
    running
  );

  // User input --------------------------------------------------------

  const parseValueFromEvent = (event): number => {
    return parseInt(event.target.value, 10);
  };

  const handleHoursChange = (event) => {
    const hours = parseValueFromEvent(event);
    setHours(hours);
    setMessage(undefined);
  };

  const handleMinutesChange = (event) => {
    const minutes = parseValueFromEvent(event);
    setMinutes(minutes);
    setMessage(undefined);
  };

  const handleSecondsChange = (event) => {
    const seconds = parseValueFromEvent(event);
    setSeconds(seconds);
    setMessage(undefined);
  };

  // User actions ------------------------------------------------------

  const start = () => {
    if (!(hours || minutes || seconds)) {
      return;
    }
    const nowMs = getNowMs();
    const totalMs = (hours * 60 * 60 + minutes * 60 + seconds) * 1000;
    setMessage(undefined);
    setStartMs(nowMs);
    setEndMs(nowMs + totalMs);
    setStarted(true);
    setRunning(true);
  };

  const reset = () => {
    setHours(0);
    setMinutes(0);
    setSeconds(0);
    setStartMs(undefined);
    setEndMs(undefined);
    setCountdown("");
    setStarted(false);
    setRunning(false);
    setPausedAt(undefined);
    setMessage(undefined);
  };

  const pause = () => {
    setPausedAt(getNowMs());
    setRunning(false);
  };

  const resume = () => {
    const resumedAt = getNowMs();
    const newEndMs = (endMs as number) + (resumedAt - (pausedAt as number));
    setPausedAt(undefined);
    setEndMs(newEndMs);
    setRunning(true);
  };

  const cancel = () => {
    setMessage(undefined);
    setEndMs(undefined);
    setStarted(false);
    setRunning(false);
  };

  const done = () => {
    setMessage("Done!");
    setEndMs(undefined);
    setStarted(false);
    setRunning(false);
    notifyDone();
  };

  // Utilities ---------------------------------------------------------

  return (
    <div className="d-flex flex-column align-items-center gap-4">
      <h1>Timer</h1>

      <Form className="d-flex align-items-end gap-2">
        {started ? (
          <div className="d-flex flex-column align-items-center gap-4">
            <div>{countdown}</div>

            {endMs && !pausedAt ? (
              <div>Ends at {msToTimeString(endMs)}</div>
            ) : null}

            {pausedAt ? <div className="text-muted">Ends at ---</div> : null}

            <div className="d-flex gap-2">
              {running ? (
                <IconButton
                  icon={<FaPause />}
                  variant="outline-secondary"
                  onClick={pause}
                >
                  Pause
                </IconButton>
              ) : (
                <IconButton
                  icon={<FaPlay />}
                  variant="outline-success"
                  onClick={resume}
                >
                  Resume
                </IconButton>
              )}

              <IconButton
                icon={<FaStop />}
                variant="outline-danger"
                onClick={cancel}
              >
                Cancel
              </IconButton>
            </div>
          </div>
        ) : (
          <>
            <Form.Group>
              <Form.Label htmlFor="hours">Hours</Form.Label>
              <Form.Select
                id="hours"
                value={hours}
                onChange={handleHoursChange}
              >
                {numberOptions(24)}
              </Form.Select>
            </Form.Group>

            <Form.Group>
              <Form.Label htmlFor="minutes">Minutes</Form.Label>
              <Form.Select
                id="minutes"
                value={minutes}
                onChange={handleMinutesChange}
              >
                {numberOptions(60)}
              </Form.Select>
            </Form.Group>

            <Form.Group>
              <Form.Label htmlFor="seconds">Seconds</Form.Label>
              <Form.Select
                id="seconds"
                value={seconds}
                onChange={handleSecondsChange}
              >
                {numberOptions(60)}
              </Form.Select>
            </Form.Group>

            <Button
              title="Start timer"
              variant="outline-success"
              disabled={!(hours || minutes || seconds)}
              onClick={start}
            >
              &gt;
            </Button>

            <Button
              title="Reset hours, minutes, and seconds"
              variant="outline-secondary"
              disabled={!(hours || minutes || seconds)}
              onClick={reset}
            >
              &times;
            </Button>
          </>
        )}
      </Form>

      {started && startMs && endMs ? (
        <div className="bg-light w-100">
          <ProgressBar
            min={Math.round(startMs / 10)}
            max={Math.round(endMs / 10)}
            now={Math.round(getNowMs() / 10)}
            striped={true}
          />
        </div>
      ) : null}

      {message ? <p className="lead">{message}</p> : null}
    </div>
  );
}

function divmod(a: number, b: number): [number, number] {
  return [Math.floor(a / b), a % b];
}

function getNowMs() {
  return new Date().getTime();
}

function msToTimeString(ms: number) {
  return new Date(ms).toLocaleTimeString();
}

function getCountdown(nowMs, endMs) {
  const remainingSeconds = Math.round((endMs - nowMs) / 1000);
  const [h, restM] = divmod(remainingSeconds, 3600);
  const [m, s] = divmod(restM, 60);
  const parts: string[] = [];
  if (h) {
    parts.push(`${h}h`);
  }
  if (h || m) {
    parts.push(`${m}m`);
  }
  parts.push(`${s}s`);
  return parts.join(" ");
}

function notifyDone() {
  if (typeof window.Notification === "undefined") {
    return;
  }

  const title = "Timer";
  const body = "Timer finished!";

  switch (Notification.permission) {
    case "denied":
      return;
    case "granted":
      new Notification(title, { body });
      return;
    default:
      Notification.requestPermission().then((permission) => {
        if (permission === "granted") {
          new Notification(title, { body });
        }
      });
  }
}

function numberOptions(count) {
  return Array.from(range(count)).map((n) => (
    <option key={n} value={n}>
      {n}
    </option>
  ));
}

function* range(quantity, start = 0) {
  const end = start + quantity;
  for (let i = start; i < end; ++i) {
    yield i;
  }
}

function useInterval(callback, delay, condition) {
  const savedCallback = useRef<() => void>();

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (condition) {
      const tick = () => {
        if (savedCallback.current) {
          savedCallback.current();
        }
      };
      const id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay, condition]);
}
