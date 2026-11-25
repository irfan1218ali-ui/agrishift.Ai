"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { BarChart3, ClipboardList, LogOut, Menu, Sprout } from "lucide-react";
import { Brand } from "@/components/brand";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

type Session = { authenticated: boolean; email?: string | null; role?: string };

export function ExpertShell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const router = useRouter();
  const [session, setSession] = useState<Session | null>(null);
  const [mobileMenu, setMobileMenu] = useState(false);
  useEffect(() => {
    api.expertMe().then((value) => setSession(value)).catch(() => router.replace(`/expert/login?next=${encodeURIComponent(path)}`));
  }, [path, router]);
  const logout = async () => { try { await api.expertLogout(); } finally { router.replace("/expert/login"); } };
  if (!session?.authenticated) return <main className="grid min-h-svh place-items-center text-sm text-slate-600" role="status">Checking expert session…</main>;
  const links = [{ href: "/expert/dashboard", label: "Overview", icon: BarChart3 }, { href: "/expert/dashboard#analyses", label: "Analyses", icon: ClipboardList }];
  return <div className="expert-app">
    <div className="mobile-expert-bar"><Brand href="/expert/dashboard" /><Button size="icon" variant="ghost" aria-label="Toggle expert navigation" aria-expanded={mobileMenu} onClick={() => setMobileMenu((value) => !value)}><Menu size={19} /></Button></div>
    {mobileMenu && <nav className="expert-mobile-menu" aria-label="Expert navigation">{links.map((item) => <Link key={item.href} href={item.href} onClick={() => setMobileMenu(false)}><item.icon size={17} />{item.label}</Link>)}<button type="button" onClick={logout}><LogOut size={17} />Sign out</button></nav>}
    <div className="expert-shell">
      <aside className="expert-sidebar">
        <Brand href="/expert/dashboard" />
        <div className="expert-nav-group"><div className="expert-nav-caption">Expert workspace</div><nav className="expert-nav" aria-label="Expert workspace">{links.map((item) => <Link key={item.href} href={item.href} className={path.startsWith(item.href.split("#")[0]) ? "active" : ""}><item.icon size={17} />{item.label}</Link>)}</nav></div>
        <div className="expert-sidebar-bottom"><div className="mb-3 flex items-center gap-2 px-2 text-xs text-slate-600"><span className="grid size-8 place-items-center rounded-full bg-green-100 text-green-900"><Sprout size={16} /></span><span className="min-w-0 truncate">{session.email}</span></div><Button variant="ghost" className="w-full justify-start" onClick={logout}><LogOut size={16} />Sign out</Button></div>
      </aside>
      <div className="min-w-0">{children}</div>
    </div>
  </div>;
}
