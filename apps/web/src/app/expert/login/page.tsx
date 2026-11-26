"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { ArrowLeft, KeyRound, ShieldCheck } from "lucide-react";
import { Brand } from "@/components/brand";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

const photo = "https://upload.wikimedia.org/wikipedia/commons/9/99/Farm_fields_of_Pakistan_in_Monsoon_season.jpg";

export default function ExpertLoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [configured, setConfigured] = useState<boolean | null>(null);
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    let alive = true;
    fetch("/api/expert/auth/me", { cache: "no-store" }).then(async (response) => {
      if (!alive) return;
      const payload = await response.json().catch(() => null);
      const apiUnavailable = payload?.error?.code === "API_UNAVAILABLE";
      setConfigured(response.status !== 503 || apiUnavailable);
      if (apiUnavailable) setError("The expert API could not be reached. Start the backend and try again.");
      if (response.ok) window.location.assign("/expert/dashboard");
    }).catch(() => { if (alive) { setConfigured(true); setError("The expert API could not be reached. Start the backend and try again."); } });
    return () => { alive = false; };
  }, []);
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setBusy(true); setError("");
    try {
      await api.expertLogin(email, password);
      const next = new URLSearchParams(window.location.search).get("next");
      window.location.assign(next?.startsWith("/expert") ? next : "/expert/dashboard");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Expert sign-in failed."); }
    setBusy(false);
  };
  return <main className="login-page">
    <section className="login-visual"><Brand /><div className="login-photo"><img src={photo} alt="Illustrative crop field in Punjab, Pakistan" /></div><p className="max-w-md text-sm text-slate-600">Review the evidence behind field rotation comparisons. The photograph is illustrative and is not an analyzed field.</p></section>
    <section className="login-main">
      <form className="login-form" onSubmit={submit}>
        <Link href="/" className="mb-6 inline-flex min-h-11 items-center gap-2 text-sm font-semibold text-slate-600"><ArrowLeft size={16} />Back to AgriShift</Link>
        <div className="mb-5 grid size-12 place-items-center rounded-2xl bg-green-100 text-green-900"><ShieldCheck size={22} /></div>
        <p className="section-kicker">Single expert account</p><h1>Expert sign in</h1><p>Access saved analyses from this browser and review the available field evidence.</p>
        <div className="form-stack">
          <div><label className="field-label" htmlFor="email">Email</label><Input id="email" type="email" autoComplete="username" value={email} onChange={(event) => setEmail(event.target.value)} required /></div>
          <div><label className="field-label" htmlFor="password">Password</label><Input id="password" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required /></div>
        {configured === false && <div className="login-status" role="status">Expert login is not configured. Set <code>EXPERT_EMAIL</code>, <code>EXPERT_PASSWORD_HASH</code>, and <code>EXPERT_SESSION_SECRET</code> in the backend environment, then restart the API.</div>}
          {error && <p className="error-text" role="alert">{error}</p>}
          <Button size="lg" type="submit" disabled={busy || configured === false}><KeyRound size={16} />{busy ? "Signing in…" : "Open expert workspace"}</Button>
        </div>
        <div className="login-status mt-5">Expert credentials remain on the server. The farmer analysis flow does not require an account.</div>
      </form>
    </section>
  </main>;
}
