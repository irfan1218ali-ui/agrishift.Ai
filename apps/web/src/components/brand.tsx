import Link from "next/link";
import { Sprout } from "lucide-react";

export function Brand({ href = "/" }: { href?: string }) {
  return (
    <Link className="brand-link" href={href} aria-label="AgriShift AI home">
      <span className="brand-symbol"><Sprout size={22} strokeWidth={2.1} /></span>
      <span>AgriShift <span className="font-medium">AI</span></span>
    </Link>
  );
}
