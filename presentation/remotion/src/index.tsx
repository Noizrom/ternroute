import "@fontsource-variable/bricolage-grotesque";
import "@fontsource/ibm-plex-mono/400.css";
import "@fontsource/ibm-plex-mono/600.css";

import type {CSSProperties, ReactNode} from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  Sequence,
  interpolate,
  registerRoot,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const FPS = 30;
const WIDTH = 1920;
const HEIGHT = 1080;
const DURATION = 2400;

const C = {
  background: "#050d16",
  panel: "#0a1826",
  panelStrong: "#0e2032",
  text: "#f3f7fb",
  muted: "#8da2b7",
  faint: "#294157",
  cyan: "#37d7ff",
  teal: "#30e6a0",
  violet: "#aa8cff",
  amber: "#ffb354",
  red: "#ff6278",
};

const display: CSSProperties = {
  fontFamily: '"Bricolage Grotesque Variable", sans-serif',
};

const mono: CSSProperties = {
  fontFamily: '"IBM Plex Mono", monospace',
};

const clamp = {
  extrapolateLeft: "clamp" as const,
  extrapolateRight: "clamp" as const,
};

const scenes = [
  {from: 0, duration: 210, label: "Premise"},
  {from: 210, duration: 360, label: "Classify"},
  {from: 570, duration: 360, label: "Select"},
  {from: 930, duration: 330, label: "Dispatch"},
  {from: 1260, duration: 330, label: "Bound"},
  {from: 1590, duration: 390, label: "Reroute"},
  {from: 1980, duration: 420, label: "Observe"},
] as const;

const appear = (frame: number, delay = 0, duration = 24) =>
  interpolate(frame, [delay, delay + duration], [0, 1], {
    ...clamp,
    easing: Easing.out(Easing.cubic),
  });

const sceneOpacity = (frame: number, duration: number) =>
  Math.min(appear(frame, 0, 16), interpolate(frame, [duration - 18, duration], [1, 0], clamp));

const lift = (progress: number, distance = 34): CSSProperties => ({
  opacity: progress,
  transform: `translateY(${(1 - progress) * distance}px)`,
});

const tagStyle = (color: string): CSSProperties => ({
  ...mono,
  display: "inline-flex",
  alignItems: "center",
  height: 42,
  padding: "0 16px",
  border: `1px solid ${color}70`,
  color,
  background: `${color}10`,
  fontSize: 18,
  fontWeight: 600,
  letterSpacing: "0.025em",
  clipPath: "polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px))",
});

const Tag = ({children, color = C.cyan}: {children: ReactNode; color?: string}) => (
  <span style={tagStyle(color)}>{children}</span>
);

const CutPanel = ({
  children,
  accent = C.faint,
  style,
}: {
  children: ReactNode;
  accent?: string;
  style?: CSSProperties;
}) => (
  <div
    style={{
      position: "relative",
      background: "linear-gradient(145deg, rgba(14,32,50,.94), rgba(7,18,30,.9))",
      border: `1px solid ${accent}90`,
      clipPath: "polygon(0 0, calc(100% - 24px) 0, 100% 24px, 100% 100%, 24px 100%, 0 calc(100% - 24px))",
      boxShadow: `inset 0 0 36px ${accent}0b`,
      ...style,
    }}
  >
    <div style={{position: "absolute", top: 0, left: 0, width: 70, height: 3, background: accent}} />
    {children}
  </div>
);

const RoutePath = ({
  d,
  progress,
  color = C.cyan,
  width = 4,
  dashed = false,
}: {
  d: string;
  progress: number;
  color?: string;
  width?: number;
  dashed?: boolean;
}) => (
  <svg viewBox="0 0 1920 1080" style={{position: "absolute", inset: 0, width: "100%", height: "100%"}}>
    <path d={d} fill="none" stroke={C.faint} strokeWidth={width} opacity={0.45} />
    <path
      d={d}
      fill="none"
      stroke={color}
      strokeWidth={width}
      strokeLinecap="round"
      pathLength={1}
      strokeDasharray={dashed ? "0.025 0.02" : 1}
      strokeDashoffset={dashed ? 0 : 1 - progress}
      style={{filter: `drop-shadow(0 0 8px ${color}80)`}}
    />
  </svg>
);

const Packet = ({x, y, color = C.cyan, label}: {x: number; y: number; color?: string; label?: string}) => (
  <div style={{position: "absolute", left: x, top: y, transform: "translate(-50%, -50%)"}}>
    <div
      style={{
        width: 25,
        height: 25,
        transform: "rotate(45deg)",
        border: `3px solid ${color}`,
        background: C.background,
        boxShadow: `0 0 28px ${color}`,
      }}
    />
    {label ? (
      <div style={{...mono, position: "absolute", top: 28, left: 18, color, fontSize: 15, whiteSpace: "nowrap"}}>
        {label}
      </div>
    ) : null}
  </div>
);

const Backdrop = () => {
  const frame = useCurrentFrame();
  const x = 50 + Math.sin(frame / 130) * 8;
  const y = 30 + Math.cos(frame / 170) * 7;
  return (
    <AbsoluteFill style={{backgroundColor: C.background, overflow: "hidden"}}>
      <div
        style={{
          position: "absolute",
          inset: -180,
          background: `radial-gradient(circle at ${x}% ${y}%, ${C.cyan}17 0, transparent 30%), radial-gradient(circle at 80% 80%, ${C.violet}12 0, transparent 28%)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.28,
          backgroundImage: `linear-gradient(${C.faint}55 1px, transparent 1px), linear-gradient(90deg, ${C.faint}55 1px, transparent 1px)`,
          backgroundSize: "80px 80px",
          transform: `translate(${-(frame % 80)}px, ${-(frame % 80)}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.22,
          backgroundImage: "radial-gradient(rgba(255,255,255,.16) .6px, transparent .8px)",
          backgroundSize: "5px 5px",
          mixBlendMode: "soft-light",
        }}
      />
    </AbsoluteFill>
  );
};

const Chrome = () => {
  const frame = useCurrentFrame();
  const seconds = frame / FPS;
  const active = scenes.findIndex(({from, duration}) => frame >= from && frame < from + duration);
  return (
    <>
      <div style={{position: "absolute", top: 38, left: 56, display: "flex", alignItems: "center", gap: 17}}>
        <div style={{width: 16, height: 16, border: `3px solid ${C.cyan}`, transform: "rotate(45deg)", boxShadow: `0 0 14px ${C.cyan}`}} />
        <div style={{...display, color: C.text, fontSize: 24, fontWeight: 700, letterSpacing: "-.02em"}}>TERNROUTE</div>
        <div style={{...mono, color: C.muted, fontSize: 14}}>/ ROUTER TRACE</div>
      </div>
      <div style={{position: "absolute", top: 42, right: 58, ...mono, color: C.muted, fontSize: 15}}>
        {String(Math.floor(seconds / 60)).padStart(2, "0")}:{String(Math.floor(seconds % 60)).padStart(2, "0")} / 01:20
      </div>
      <div style={{position: "absolute", right: 58, top: 160, display: "flex", flexDirection: "column", gap: 17}}>
        {scenes.map((scene, index) => (
          <div key={scene.label} style={{display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 12}}>
            <span style={{...mono, color: index === active ? C.text : C.muted, fontSize: 13, opacity: index === active ? 1 : 0.45}}>
              {scene.label.toUpperCase()}
            </span>
            <span style={{width: index === active ? 34 : 12, height: 2, background: index === active ? C.cyan : C.faint}} />
          </div>
        ))}
      </div>
      <div style={{position: "absolute", left: 56, right: 56, bottom: 28, height: 2, background: C.faint}}>
        <div style={{height: "100%", width: `${(frame / DURATION) * 100}%`, background: C.cyan, boxShadow: `0 0 12px ${C.cyan}`}} />
      </div>
    </>
  );
};

const SceneFrame = ({
  number,
  title,
  eyebrow,
  caption,
  accent,
  duration,
  children,
}: {
  number: string;
  title: string;
  eyebrow: string;
  caption: string;
  accent: string;
  duration: number;
  children: ReactNode;
}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{opacity: sceneOpacity(frame, duration)}}>
      <div style={{position: "absolute", left: 58, top: 120, display: "flex", alignItems: "flex-start", gap: 22}}>
        <span style={{...mono, color: accent, fontSize: 18, paddingTop: 11}}>{number}</span>
        <div>
          <div style={{...mono, color: C.muted, fontSize: 14, letterSpacing: ".14em", marginBottom: 6}}>{eyebrow.toUpperCase()}</div>
          <div style={{...display, color: C.text, fontSize: 48, lineHeight: 1, fontWeight: 680, letterSpacing: "-.035em"}}>{title}</div>
        </div>
      </div>
      {children}
      <div
        style={{
          position: "absolute",
          left: 58,
          right: 330,
          bottom: 62,
          minHeight: 58,
          display: "flex",
          alignItems: "center",
          borderTop: `1px solid ${C.faint}`,
          background: "linear-gradient(90deg, rgba(5,13,22,.96), rgba(5,13,22,.45))",
        }}
      >
        <div style={{width: 4, height: 34, background: accent, marginRight: 18, boxShadow: `0 0 12px ${accent}`}} />
        <div style={{...display, color: C.text, fontSize: 25, fontWeight: 470}}>{caption}</div>
      </div>
    </AbsoluteFill>
  );
};

const Intro = () => {
  const frame = useCurrentFrame();
  const title = spring({frame, fps: FPS, config: {damping: 17, stiffness: 95, mass: 0.8}, durationInFrames: 42});
  const route = appear(frame, 58, 82);
  const packetProgress = interpolate(frame, [70, 175], [0, 1], clamp);
  const x = interpolate(packetProgress, [0, 0.45, 1], [220, 940, 1660]);
  const y = interpolate(packetProgress, [0, 0.45, 1], [720, 620, 710]);
  return (
    <AbsoluteFill style={{opacity: sceneOpacity(frame, 210)}}>
      <RoutePath d="M 220 720 C 520 720, 620 620, 940 620 S 1360 710, 1660 710" progress={route} color={C.cyan} width={5} />
      <div style={{position: "absolute", left: 112, top: 180, ...lift(title, 48)}}>
        <div style={{...mono, color: C.violet, fontSize: 17, letterSpacing: ".18em", marginBottom: 20}}>IMPLEMENTED ARCHITECTURE</div>
        <div style={{...display, color: C.text, fontSize: 126, lineHeight: 0.84, fontWeight: 760, letterSpacing: "-.065em"}}>
          ROUTE
          <br />
          BEFORE
          <br />
          <span style={{color: C.cyan}}>INFERENCE.</span>
        </div>
      </div>
      <div style={{position: "absolute", right: 180, top: 255, width: 480, ...lift(appear(frame, 32, 26), 30)}}>
        <div style={{...display, color: C.text, fontSize: 31, lineHeight: 1.25}}>One request stream.<br />Different workloads.<br />Exact destinations.</div>
        <div style={{...mono, color: C.muted, fontSize: 16, lineHeight: 1.8, marginTop: 28}}>regex classification<br />runtime allowlist<br />bounded remote dispatch</div>
      </div>
      {frame > 66 ? <Packet x={x} y={y} color={packetProgress > 0.48 ? C.teal : C.cyan} label="request:t-01" /> : null}
      <div style={{position: "absolute", left: 112, bottom: 86, display: "flex", gap: 14, opacity: appear(frame, 45, 25)}}>
        <Tag color={C.violet}>0 ROUTING TOKENS</Tag>
        <Tag color={C.teal}>ALLOWLIST ONLY</Tag>
        <Tag color={C.amber}>2 ATTEMPTS MAX</Tag>
      </div>
    </AbsoluteFill>
  );
};

const Classify = () => {
  const frame = useCurrentFrame();
  const scan = interpolate(frame, [75, 170], [0, 1], clamp);
  const categories = ["CODE_DEBUGGING", "CODE_GENERATION", "SUMMARIZATION", "NER / SENTIMENT", "MATH / LOGIC", "FACTUAL FALLBACK"];
  const active = frame > 154;
  return (
    <SceneFrame
      number="01"
      eyebrow="Local analysis"
      title="Prompt → routing metadata"
      caption="Ordered regex rules classify each task locally—without making a model call."
      accent={C.violet}
      duration={360}
    >
      <CutPanel accent={C.cyan} style={{position: "absolute", left: 92, top: 310, width: 590, height: 320, padding: 34, ...lift(appear(frame, 20), 32)}}>
        <div style={{...mono, color: C.cyan, fontSize: 15, marginBottom: 34}}>INCOMING REQUEST / t-01</div>
        <div style={{...display, color: C.text, fontSize: 38, lineHeight: 1.18, fontWeight: 570}}>“Debug and implement a fix for this Python function.”</div>
        <div style={{...mono, color: C.muted, fontSize: 14, marginTop: 32}}>app/task_analysis.py · analyze_task()</div>
        <div style={{position: "absolute", left: 0, right: 0, top: `${80 + scan * 195}px`, height: 2, background: C.cyan, boxShadow: `0 0 18px ${C.cyan}`}} />
      </CutPanel>
      <div style={{position: "absolute", left: 770, top: 292, width: 440, display: "flex", flexDirection: "column", gap: 12}}>
        {categories.map((category, index) => {
          const p = appear(frame, 64 + index * 8, 18);
          const selected = index === 0 && active;
          return (
            <div
              key={category}
              style={{
                ...mono,
                ...lift(p, 18),
                height: 58,
                display: "flex",
                alignItems: "center",
                padding: "0 20px",
                color: selected ? C.cyan : C.muted,
                borderLeft: `3px solid ${selected ? C.cyan : C.faint}`,
                background: selected ? `${C.cyan}12` : "rgba(10,24,38,.42)",
                fontSize: 17,
              }}
            >
              <span style={{opacity: 0.45, width: 40}}>{String(index + 1).padStart(2, "0")}</span>{category}
            </div>
          );
        })}
      </div>
      <CutPanel accent={C.teal} style={{position: "absolute", right: 155, top: 340, width: 410, height: 280, padding: 30, ...lift(appear(frame, 165), 24)}}>
        <div style={{...mono, color: C.teal, fontSize: 15, marginBottom: 25}}>TASK ANALYSIS</div>
        {[
          ["category", "code_debugging"],
          ["format", "code"],
          ["code_only", "true"],
          ["decision", "first match wins"],
        ].map(([key, value]) => (
          <div key={key} style={{...mono, display: "flex", justifyContent: "space-between", borderBottom: `1px solid ${C.faint}`, padding: "11px 0", fontSize: 15}}>
            <span style={{color: C.muted}}>{key}</span><span style={{color: C.text}}>{value}</span>
          </div>
        ))}
      </CutPanel>
      <div style={{position: "absolute", left: 770, top: 710, display: "flex", gap: 14, opacity: appear(frame, 205)}}>
        <Tag color={C.violet}>REGEX RULES</Tag><Tag color={C.teal}>NO API CALL</Tag><Tag color={C.cyan}>FIRST MATCH WINS</Tag>
      </div>
    </SceneFrame>
  );
};

const SelectModel = () => {
  const frame = useCurrentFrame();
  const route = appear(frame, 115, 100);
  const packetProgress = interpolate(frame, [130, 245], [0, 1], clamp);
  const x = interpolate(packetProgress, [0, 0.5, 1], [315, 865, 1485]);
  const y = interpolate(packetProgress, [0, 0.5, 1], [630, 585, 500]);
  const models = [
    {name: "gemma-compact", color: C.teal},
    {name: "kimi-next-code", color: C.cyan},
    {name: "minimax-general", color: C.amber},
  ];
  return (
    <SceneFrame
      number="02"
      eyebrow="Policy boundary"
      title="Choose inside the allowlist"
      caption="Profiles rank candidates, but the runtime allowlist remains the hard boundary."
      accent={C.teal}
      duration={360}
    >
      <div style={{position: "absolute", left: 95, top: 315, width: 495, ...lift(appear(frame, 20), 30)}}>
        <div style={{...mono, color: C.muted, fontSize: 15, marginBottom: 18}}>CATEGORY PROFILE</div>
        <div style={{...display, color: C.text, fontSize: 70, fontWeight: 710, letterSpacing: "-.04em"}}>CODE</div>
        <div style={{...mono, color: C.cyan, fontSize: 25, marginTop: 15}}>r"kimi.*code"</div>
        <div style={{...mono, color: C.muted, fontSize: 15, marginTop: 34, lineHeight: 1.8}}>01 preference pattern<br />02 exact allowlist scan<br />03 first match returned</div>
      </div>
      <CutPanel accent={C.teal} style={{position: "absolute", left: 720, top: 270, width: 970, height: 430, padding: 34, ...lift(appear(frame, 42), 26)}}>
        <div style={{...mono, color: C.teal, fontSize: 15, letterSpacing: ".08em"}}>RUNTIME ALLOWED_MODELS</div>
        <div style={{display: "flex", gap: 20, marginTop: 42}}>
          {models.map((model, index) => (
            <div
              key={model.name}
              style={{
                flex: 1,
                height: 185,
                border: `1px solid ${model.color}80`,
                background: index === 1 && frame > 215 ? `${model.color}1c` : "rgba(5,13,22,.6)",
                padding: 22,
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                boxShadow: index === 1 && frame > 215 ? `0 0 34px ${model.color}25` : "none",
              }}
            >
              <div style={{...mono, color: model.color, fontSize: 15}}>0{index + 1}</div>
              <div style={{...display, color: C.text, fontSize: 24, fontWeight: 600}}>{model.name}</div>
              <div style={{...mono, color: C.muted, fontSize: 12}}>{index === 1 ? "PROFILE MATCH" : "APPROVED CANDIDATE"}</div>
            </div>
          ))}
        </div>
        <div style={{...mono, color: C.muted, fontSize: 14, marginTop: 35}}>no pattern match → first remaining exact value</div>
      </CutPanel>
      <RoutePath d="M 315 630 C 580 630, 620 585, 865 585 S 1260 500, 1485 500" progress={route} color={C.cyan} width={5} />
      {frame > 126 ? <Packet x={x} y={y} color={C.cyan} label={packetProgress > 0.82 ? "selected" : "code_debugging"} /> : null}
      <div style={{position: "absolute", left: 742, top: 742, display: "flex", gap: 16, opacity: appear(frame, 245)}}>
        <Tag color={C.teal}>EXACT ID ONLY</Tag><Tag color={C.cyan}>NO MODEL NAME CONSTRUCTION</Tag>
      </div>
    </SceneFrame>
  );
};

const Dispatch = () => {
  const frame = useCurrentFrame();
  const assemble = appear(frame, 45, 70);
  const route = appear(frame, 145, 70);
  const fields = [
    ["model", '"kimi-next-code"', C.cyan],
    ["messages", "[system, user]", C.text],
    ["temperature", "0", C.teal],
    ["max_tokens", "1024", C.amber],
    ["timeout", "remaining budget", C.violet],
  ] as const;
  return (
    <SceneFrame
      number="03"
      eyebrow="Request assembly"
      title="Deterministic by construction"
      caption="The exact model, original prompt, short system prompt, and token ceiling travel together."
      accent={C.amber}
      duration={330}
    >
      <CutPanel accent={C.cyan} style={{position: "absolute", left: 120, top: 300, width: 690, height: 475, padding: 36, ...lift(assemble, 26)}}>
        <div style={{...mono, color: C.cyan, fontSize: 15, marginBottom: 28}}>POST /chat/completions</div>
        {fields.map(([key, value, color], index) => (
          <div
            key={key}
            style={{
              ...mono,
              opacity: appear(frame, 58 + index * 14),
              transform: `translateX(${(1 - appear(frame, 58 + index * 14)) * -24}px)`,
              display: "grid",
              gridTemplateColumns: "180px 1fr",
              borderBottom: `1px solid ${C.faint}`,
              padding: "17px 0",
              fontSize: 18,
            }}
          >
            <span style={{color: C.muted}}>{key}</span><span style={{color}}>{value}</span>
          </div>
        ))}
      </CutPanel>
      <RoutePath d="M 810 540 C 1040 540, 1090 540, 1260 540" progress={route} color={C.amber} width={5} />
      <div style={{position: "absolute", left: 1280, top: 350, width: 430, ...lift(appear(frame, 140), 28)}}>
        <div style={{...display, color: C.amber, fontSize: 76, fontWeight: 730, letterSpacing: "-.05em"}}>FIREWORKS</div>
        <div style={{...display, color: C.text, fontSize: 33}}>Chat Completions</div>
        <div style={{...mono, color: C.muted, marginTop: 38, fontSize: 15, lineHeight: 1.9}}>Bearer auth<br />redirects disabled<br />urllib via asyncio.to_thread</div>
      </div>
      <div style={{position: "absolute", left: 955, top: 730, display: "flex", gap: 13, opacity: appear(frame, 210)}}>
        <Tag color={C.teal}>LABEL 16</Tag><Tag color={C.cyan}>FACTUAL 96</Tag><Tag color={C.violet}>SUMMARY 256</Tag><Tag color={C.amber}>CODE 1024</Tag>
      </div>
    </SceneFrame>
  );
};

const Guardrails = () => {
  const frame = useCurrentFrame();
  const taskProgress = interpolate(frame, [95, 175], [0, 1], clamp);
  const tasks = ["t-01", "t-02", "t-03", "t-04", "t-05"];
  return (
    <SceneFrame
      number="04"
      eyebrow="Execution control"
      title="Two lanes. Shared deadline."
      caption="A semaphore bounds parallel solves while task and batch budgets share one monotonic clock."
      accent={C.cyan}
      duration={330}
    >
      <div style={{position: "absolute", left: 100, top: 300, ...lift(appear(frame, 20), 20)}}>
        <div style={{...mono, color: C.muted, fontSize: 15, marginBottom: 20}}>TASK QUEUE</div>
        <div style={{display: "flex", flexDirection: "column", gap: 12}}>
          {tasks.map((task, index) => (
            <div key={task} style={{...mono, width: 190, height: 54, border: `1px solid ${C.violet}70`, color: index < 2 && frame > 145 ? C.faint : C.violet, display: "flex", alignItems: "center", paddingLeft: 20, fontSize: 16, background: `${C.violet}0d`}}>{task}</div>
          ))}
        </div>
      </div>
      <div style={{position: "absolute", left: 520, top: 288, width: 530, height: 440, borderLeft: `2px solid ${C.cyan}`, borderRight: `2px solid ${C.cyan}`, background: `${C.cyan}07`, opacity: appear(frame, 55)}}>
        <div style={{...mono, color: C.cyan, fontSize: 15, textAlign: "center", marginTop: 22}}>ASYNCIO SEMAPHORE · CAPACITY 2</div>
        {[0, 1].map((lane) => (
          <div key={lane} style={{position: "absolute", left: 46, right: 46, top: 105 + lane * 145, height: 92, borderTop: `1px solid ${C.faint}`, borderBottom: `1px solid ${C.faint}`}}>
            <span style={{...mono, color: C.muted, fontSize: 13, position: "absolute", top: 10}}>LANE 0{lane + 1}</span>
            {frame > 80 ? (
              <div style={{position: "absolute", left: 22 + taskProgress * 260, top: 39}}>
                <Tag color={C.teal}>{tasks[lane]} · ACTIVE</Tag>
              </div>
            ) : null}
          </div>
        ))}
      </div>
      <div style={{position: "absolute", left: 1150, top: 290, display: "grid", gridTemplateColumns: "repeat(2, 235px)", gap: 18, opacity: appear(frame, 135)}}>
        {[
          ["02", "concurrent solves", C.cyan],
          ["28s", "task budget", C.teal],
          ["18s", "read budget", C.amber],
          ["540s", "batch budget", C.violet],
        ].map(([value, label, color]) => (
          <CutPanel key={label} accent={color} style={{height: 170, padding: 24}}>
            <div style={{...display, color, fontSize: 58, fontWeight: 720, letterSpacing: "-.05em"}}>{value}</div>
            <div style={{...mono, color: C.muted, fontSize: 14, marginTop: 12}}>{label}</div>
          </CutPanel>
        ))}
      </div>
    </SceneFrame>
  );
};

const Reroute = () => {
  const frame = useCurrentFrame();
  const routeA = appear(frame, 55, 65);
  const reject = appear(frame, 130, 20);
  const routeB = appear(frame, 170, 90);
  const packetProgress = interpolate(frame, [180, 270], [0, 1], clamp);
  const x = interpolate(packetProgress, [0, 0.55, 1], [995, 1260, 1560]);
  const y = interpolate(packetProgress, [0, 0.55, 1], [590, 700, 570]);
  return (
    <SceneFrame
      number="05"
      eyebrow="Feedback route"
      title="Failure changes the destination"
      caption="Exclude the failed model, run selection again, and spend at most one alternate attempt."
      accent={C.red}
      duration={390}
    >
      <div style={{position: "absolute", left: 110, top: 350, width: 420, ...lift(appear(frame, 20), 20)}}>
        <Tag color={C.amber}>ATTEMPT 1</Tag>
        <div style={{...display, color: C.text, fontSize: 48, fontWeight: 650, marginTop: 24}}>minimax-general</div>
        <div style={{...mono, color: C.muted, fontSize: 14, marginTop: 18}}>selected for factual</div>
      </div>
      <RoutePath d="M 500 500 C 690 500, 725 500, 860 500" progress={routeA} color={C.amber} width={5} />
      <CutPanel accent={reject > 0.5 ? C.red : C.violet} style={{position: "absolute", left: 850, top: 350, width: 360, height: 290, padding: 28, ...lift(appear(frame, 90), 20)}}>
        <div style={{...mono, color: C.violet, fontSize: 14}}>MECHANICAL VALIDATOR</div>
        <div style={{...display, color: reject > 0.5 ? C.red : C.text, fontSize: 58, fontWeight: 730, marginTop: 30}}>{reject > 0.5 ? "REJECT" : "CHECK"}</div>
        <div style={{...mono, color: C.muted, fontSize: 13, lineHeight: 1.8, marginTop: 20}}>non-empty · labels<br />word / sentence limits<br />exact bullet count</div>
      </CutPanel>
      <RoutePath d="M 995 590 C 1090 700, 1200 720, 1260 700 S 1430 570, 1560 570" progress={routeB} color={C.teal} width={5} dashed />
      {frame > 178 ? <Packet x={x} y={y} color={C.teal} label={packetProgress > 0.78 ? "attempt 2" : "excluded"} /> : null}
      <div style={{position: "absolute", right: 120, top: 370, width: 340, opacity: appear(frame, 235)}}>
        <Tag color={C.teal}>ATTEMPT 2</Tag>
        <div style={{...display, color: C.text, fontSize: 43, fontWeight: 650, marginTop: 24}}>gemma-compact</div>
        <div style={{...mono, color: C.teal, fontSize: 14, marginTop: 18}}>next remaining model</div>
      </div>
      <div style={{position: "absolute", left: 165, top: 735, display: "flex", gap: 15, opacity: appear(frame, 260)}}>
        <Tag color={C.red}>403 / 404 · SWITCH</Tag><Tag color={C.amber}>408 / 429 / 5xx · RETRY</Tag><Tag color={C.red}>401 · FATAL</Tag>
      </div>
    </SceneFrame>
  );
};

const Observe = () => {
  const frame = useCurrentFrame();
  const terminalOut = interpolate(frame, [205, 250], [1, 0], clamp);
  const finalIn = appear(frame, 230, 38);
  const events = [
    ['{"event":"remote_attempt",', C.muted],
    [' "category":"factual", "model":"minimax-general"}', C.cyan],
    ['{"event":"remote_success", "attempt":1,', C.muted],
    [' "duration_ms":842, "total_tokens":34}', C.teal],
    ['{"event":"batch_complete", "tasks":3}', C.violet],
  ] as const;
  return (
    <SceneFrame
      number="06"
      eyebrow="Observability"
      title={frame < 230 ? "Every decision leaves a trace" : "The implemented routing loop"}
      caption={frame < 230 ? "Telemetry records the category, exact model, attempt, latency, and token usage." : "Classify locally. Constrain selection. Dispatch predictably. Reroute once."}
      accent={C.violet}
      duration={420}
    >
      <CutPanel accent={C.violet} style={{position: "absolute", left: 110, top: 300, width: 1280, height: 470, padding: 36, opacity: terminalOut * appear(frame, 18), transform: `translateY(${(1 - appear(frame, 18)) * 22}px)`}}>
        <div style={{display: "flex", gap: 9, marginBottom: 36}}>{[C.red, C.amber, C.teal].map((color) => <span key={color} style={{width: 11, height: 11, borderRadius: "50%", background: color}} />)}</div>
        <div style={{...mono, display: "flex", flexDirection: "column", gap: 18, fontSize: 20}}>
          {events.map(([line, color], index) => (
            <div key={line} style={{color, opacity: appear(frame, 48 + index * 24, 16), transform: `translateX(${(1 - appear(frame, 48 + index * 24, 16)) * -20}px)`}}>{line}</div>
          ))}
        </div>
      </CutPanel>
      <div style={{position: "absolute", left: 100, right: 220, top: 330, opacity: finalIn}}>
        <div style={{display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 54}}>
          {[
            ["01", "CLASSIFY", "regex · zero tokens", C.violet],
            ["02", "CONSTRAIN", "runtime allowlist", C.teal],
            ["03", "DISPATCH", "bounded request", C.amber],
            ["04", "VERIFY", "reroute once", C.cyan],
          ].map(([number, title, detail, color], index) => (
            <div key={title} style={{position: "relative", opacity: appear(frame, 250 + index * 14), transform: `translateY(${(1 - appear(frame, 250 + index * 14)) * 28}px)`}}>
              <div style={{...mono, color, fontSize: 15, marginBottom: 18}}>{number}</div>
              <div style={{...display, color: C.text, fontSize: 38, fontWeight: 690}}>{title}</div>
              <div style={{...mono, color: C.muted, fontSize: 14, marginTop: 12}}>{detail}</div>
              <div style={{height: 3, background: color, marginTop: 28, boxShadow: `0 0 12px ${color}`}} />
              {index < 3 ? <div style={{position: "absolute", right: -40, top: 75, color: C.faint, fontSize: 32}}>→</div> : null}
            </div>
          ))}
        </div>
        <div style={{...display, color: C.text, fontSize: 74, lineHeight: 1.05, fontWeight: 730, letterSpacing: "-.045em", marginTop: 105}}>
          LOCAL DECISIONS.<br /><span style={{color: C.teal}}>EXACT DESTINATIONS.</span><br />PREDICTABLE COST.
        </div>
        <div style={{position: "absolute", right: 20, bottom: 20}}><Tag color={C.violet}>REMOTE ROUTING BASELINE</Tag></div>
      </div>
    </SceneFrame>
  );
};

const TernRouteModern = () => (
  <AbsoluteFill style={{backgroundColor: C.background}}>
    <Backdrop />
    <Sequence from={0} durationInFrames={210}><Intro /></Sequence>
    <Sequence from={210} durationInFrames={360}><Classify /></Sequence>
    <Sequence from={570} durationInFrames={360}><SelectModel /></Sequence>
    <Sequence from={930} durationInFrames={330}><Dispatch /></Sequence>
    <Sequence from={1260} durationInFrames={330}><Guardrails /></Sequence>
    <Sequence from={1590} durationInFrames={390}><Reroute /></Sequence>
    <Sequence from={1980} durationInFrames={420}><Observe /></Sequence>
    <Chrome />
  </AbsoluteFill>
);

const RemotionRoot = () => (
  <Composition
    id="TernRouteModern"
    component={TernRouteModern}
    durationInFrames={DURATION}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);

registerRoot(RemotionRoot);
