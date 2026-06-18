"use client";

import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

const VETO = new THREE.Color("#f87171");
const REVISION = new THREE.Color("#fbbf24");
const APPROVE = new THREE.Color("#34d399");
const IDLE = new THREE.Color("#4f8cff");

type Phase = "idle" | "running";

function colorForT(t: number, target: THREE.Color) {
  if (t < 0.38) target.copy(IDLE);
  else if (t < 0.5) target.lerpColors(IDLE, VETO, (t - 0.38) / 0.12);
  else if (t < 0.78) target.lerpColors(VETO, REVISION, (t - 0.5) / 0.28);
  else target.lerpColors(REVISION, APPROVE, (t - 0.78) / 0.22);
}

function pointOnLoop(t: number, out: THREE.Vector3) {
  const a = t * Math.PI * 2 - Math.PI / 2;
  out.set(Math.cos(a) * 1.7, Math.sin(a) * 0.95, 0);
}

function Orb({ phase }: { phase: Phase }) {
  const mesh = useRef<THREE.Mesh>(null);
  const light = useRef<THREE.PointLight>(null);
  const mat = useRef<THREE.MeshStandardMaterial>(null);
  const t = useRef(0);
  const pos = useMemo(() => new THREE.Vector3(), []);
  const col = useMemo(() => new THREE.Color(), []);

  useFrame((_, delta) => {
    if (phase === "running") t.current = (t.current + delta * 0.16) % 1;
    pointOnLoop(t.current, pos);
    if (mesh.current) mesh.current.position.copy(pos);
    if (light.current) light.current.position.copy(pos);

    if (phase === "idle") col.copy(IDLE);
    else colorForT(t.current, col);

    if (mat.current) {
      mat.current.color.copy(col);
      mat.current.emissive.copy(col);
    }
    if (light.current) light.current.color.copy(col);

    const pulse = 1 + Math.sin(_.clock.elapsedTime * 4) * 0.08;
    if (mesh.current) mesh.current.scale.setScalar(pulse);
  });

  return (
    <group>
      <mesh ref={mesh}>
        <sphereGeometry args={[0.26, 32, 32]} />
        <meshStandardMaterial
          ref={mat}
          emissiveIntensity={1.6}
          roughness={0.25}
          metalness={0.1}
        />
      </mesh>
      <pointLight ref={light} intensity={6} distance={6} />
    </group>
  );
}

function LoopTrack() {
  const points = useMemo(() => {
    const p = new THREE.Vector3();
    const arr: THREE.Vector3[] = [];
    for (let i = 0; i <= 96; i++) {
      pointOnLoop(i / 96, p);
      arr.push(p.clone());
    }
    return arr;
  }, []);
  const geom = useMemo(() => new THREE.BufferGeometry().setFromPoints(points), [points]);
  return (
    <line>
      <primitive object={geom} attach="geometry" />
      <lineBasicMaterial color="#243049" transparent opacity={0.9} />
    </line>
  );
}

function Node({ t, color }: { t: number; color: string }) {
  const pos = useMemo(() => {
    const v = new THREE.Vector3();
    pointOnLoop(t, v);
    return v;
  }, [t]);
  return (
    <mesh position={pos}>
      <sphereGeometry args={[0.075, 16, 16]} />
      <meshBasicMaterial color={color} />
    </mesh>
  );
}

export default function VetoLoopCanvas({ phase }: { phase: Phase }) {
  return (
    <Canvas
      camera={{ position: [0, 0, 4.2], fov: 45 }}
      gl={{ alpha: true, antialias: true }}
      style={{ background: "transparent" }}
      dpr={[1, 2]}
    >
      <ambientLight intensity={0.5} />
      <LoopTrack />
      <Node t={0} color="#4f8cff" />
      <Node t={0.44} color="#f87171" />
      <Node t={0.86} color="#34d399" />
      <Orb phase={phase} />
    </Canvas>
  );
}
