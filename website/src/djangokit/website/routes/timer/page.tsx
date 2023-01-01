import { useEffect, useRef, useState } from "react";

import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";

import { FaPause, FaPlay, FaStop } from "react-icons/fa";

import { IconButton } from "../../components";
import { useInterval, useRequestAnimationFrame } from "../../hooks";
import { range } from "../../utils";

const TICK_MS = 50;
const DEFAULT_HOURS = ENV === "development" ? 0 : 0;
const DEFAULT_MINUTES = ENV === "development" ? 0 : 0;
const DEFAULT_SECONDS = ENV === "development" ? 8 : 0;
const HAS_NOTIFICATION = typeof window.Notification !== "undefined";

export default function Page() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // User input
  const [hours, setHours] = useState(0);
  const [minutes, setMinutes] = useState(0);
  const [seconds, setSeconds] = useState(0);

  const [nowMs, setNowMs] = useState<number>();
  const [endMs, setEndMs] = useState<number>();
  const [countdown, setCountdown] = useState("");
  const [started, setStarted] = useState(false);
  const [running, setRunning] = useState(false);
  const [pausedAt, setPausedAt] = useState<number>();
  const [message, setMessage] = useState<string>();
  const [requestedNotificationPermission, setRequestedNotificationPermission] =
    useState(false);

  const totalMs = (hours * 60 * 60 + minutes * 60 + seconds) * 1000;

  useEffect(() => {
    setHours(DEFAULT_HOURS);
    setMinutes(DEFAULT_MINUTES);
    setSeconds(DEFAULT_SECONDS);
  }, []);

  useInterval(
    () => {
      const nowMs = getNowMs();
      setNowMs(nowMs);
      if (nowMs < (endMs as number)) {
        setCountdown(getCountdown(nowMs, endMs));
      } else {
        setCountdown("0");
        done();
      }
    },
    running && endMs,
    TICK_MS
  );

  useRequestAnimationFrame(() => {
    const canvas = canvasRef.current as HTMLCanvasElement;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const [w, h] = [canvas.width, canvas.height];
    const remainingMs = (endMs as number) - (nowMs as number);
    const elapsedMs = totalMs - remainingMs;
    const percentage = elapsedMs / totalMs;

    if (!endMs) {
      ctx.clearRect(0, 0, w, h);
      return;
    }

    if (!running) {
      return;
    }

    ctx.clearRect(0, 0, w, h);

    ctx.beginPath();
    ctx.fillStyle = "white";
    ctx.rect(0, 1, percentage * w, 14);
    ctx.fill();

    ctx.beginPath();
    ctx.strokeStyle = "black";
    ctx.moveTo(0, 0);
    ctx.lineTo(percentage * w, 0);
    ctx.moveTo(0, 16);
    ctx.lineTo(percentage * w, 16);
    ctx.stroke();
  }, canvasRef.current && totalMs && nowMs && endMs && running);

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
    requestNotificationPermission().finally(() => {
      const nowMs = getNowMs();
      const totalMs = (hours * 60 * 60 + minutes * 60 + seconds) * 1000;
      setMessage(undefined);
      setNowMs(nowMs);
      setEndMs(nowMs + totalMs);
      setStarted(true);
      setRunning(true);
    });
  };

  const reset = () => {
    setHours(0);
    setMinutes(0);
    setSeconds(DEFAULT_SECONDS);
    setNowMs(undefined);
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
    setNowMs(undefined);
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
    setMessage(`Timer finished at ${msToTimeString(getNowMs())}`);
    setStarted(false);
    setRunning(false);
    if (HAS_NOTIFICATION && Notification.permission === "granted") {
      new Notification("Timer", { body: "Timer finished!" });
    }
  };

  const requestNotificationPermission = () => {
    const perm = window.Notification?.permission;
    if (!HAS_NOTIFICATION) {
      Promise.resolve("window.Notification is undefined");
    }
    if (requestedNotificationPermission) {
      return Promise.resolve("already requested");
    }
    if (perm === "granted" || perm === "denied") {
      return Promise.resolve(`already ${perm}`);
    }
    setRequestedNotificationPermission(true);
    return Notification.requestPermission();
  };

  return (
    <div
      ref={containerRef}
      className="d-flex flex-column align-items-center gap-4"
    >
      <h1>Timer</h1>

      <Form className="d-flex align-items-end gap-2">
        {started ? (
          <div className="d-flex flex-column align-items-center gap-2">
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

      {containerRef.current ? (
        <canvas
          ref={canvasRef}
          width={containerRef.current.clientWidth}
          height={16}
        ></canvas>
      ) : null}

      {running ? <p className="lead">{countdown}</p> : null}
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

function numberOptions(count) {
  return Array.from(range(count)).map((n) => (
    <option key={n} value={n}>
      {n}
    </option>
  ));
}
