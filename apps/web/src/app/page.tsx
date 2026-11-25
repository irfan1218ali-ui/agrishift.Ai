import Link from "next/link";
import { ArrowDownRight, ArrowRight, Check, Droplets, Map, Satellite, ShieldCheck, Sprout, Trees, Wheat } from "lucide-react";
import { Brand } from "@/components/brand";
import { LandingDataModeBadge } from "@/components/landing-data-mode";
import { OpenSavedAnalysis } from "@/components/open-saved-analysis";
import { Button } from "@/components/ui/button";

const fieldPhoto = "https://upload.wikimedia.org/wikipedia/commons/9/99/Farm_fields_of_Pakistan_in_Monsoon_season.jpg";

export default function LandingPage() {
  return (
    <main>
      <div className="site-nav-wrap">
        <nav className="site-nav frame" aria-label="Main navigation">
          <Brand />
          <div className="site-links">
            <a href="#how">How it works</a>
            <a href="#sources">Data sources</a>
            <a href="#rotation">Crop rotation</a>
          </div>
          <div className="nav-tools">
            <div className="lang-mini" aria-label="Choose analysis language">
              <Link href="/analyze?lang=en" aria-label="English">EN</Link>
              <Link href="/analyze?lang=ur" aria-label="Urdu">اردو</Link>
              <Link href="/analyze?lang=sd" aria-label="Sindhi">سنڌي</Link>
            </div>
            <Button asChild className="button-primary"><Link href="/analyze?lang=en">Analyze my field <ArrowRight size={16} /></Link></Button>
          </div>
        </nav>
      </div>

      <section className="landing-hero frame">
        <div className="hero-copy">
          <div className="hero-location"><Map size={16} /> Hyderabad pilot · Sindh, Pakistan <LandingDataModeBadge /></div>
          <h1 className="hero-title">Better rotations start here.</h1>
          <p className="hero-description">Compare three crop sequences using satellite observations, climate history, and your own water and soil conditions.</p>
          <div className="hero-actions">
            <Button asChild size="lg"><Link href="/analyze?lang=en">Analyze my field <ArrowRight size={17} /></Link></Button>
            <Button asChild variant="secondary" size="lg"><a href="#sources">Explore demo <ArrowDownRight size={17} /></a></Button>
          </div>
          <OpenSavedAnalysis />
          <div className="hero-proof">
            <span><Check size={16} /> 149 validated pilot points</span>
            <span><Check size={16} /> Farmer does not need an account</span>
          </div>
        </div>
        <div className="hero-photo-wrap" aria-label="Illustrative photograph of farmland in Pakistan">
          <img className="hero-photo" src={fieldPhoto} alt="Mustard fields in Punjab, Pakistan during the monsoon season" />
          <div className="hero-photo-shade" />
          <div className="hero-data-card" data-ui="field-evidence">
            <div className="hero-card-title"><span>Hyderabad pilot coverage</span><Satellite size={17} color="#166534" /></div>
            <div className="hero-card-line"><span>Environmental points</span><strong>149</strong></div>
            <div className="hero-card-line"><span>Satellite & terrain layers</span><strong>30 m</strong></div>
            <div className="hero-card-line"><span>Rotation choices</span><strong>3 options</strong></div>
          </div>
          <div className="hero-photo-caption">Illustrative field photograph; this is not a field analyzed by AgriShift.</div>
        </div>
      </section>

      <section id="how" className="section-space frame">
        <div className="section-topline">
          <div>
            <p className="section-kicker">A short, farmer-led check</p>
            <h2 className="section-heading">From field pin to rotation choices.</h2>
          </div>
          <p className="section-intro">Share only the details that shape a rotation. AgriShift compares the sequences and shows what needs local review.</p>
        </div>
        <div className="section-grid-3">
          <article className="step-card"><span className="step-card-number">1</span><h3>Choose the field</h3><p>Use your current location, find a nearby town, or drop a pin on the map. Analysis is limited to the validated Hyderabad pilot area.</p></article>
          <article className="step-card"><span className="step-card-number">2</span><h3>Share what you know</h3><p>Select recent crops, water availability, and visible soil conditions. You can mark an answer as unknown.</p></article>
          <article className="step-card"><span className="step-card-number">3</span><h3>Compare three plans</h3><p>Review your current rotation, a balanced alternative, and an option shaped by your chosen priority.</p></article>
        </div>
      </section>

      <section id="sources" className="section-space" style={{ background: "#edf4ee" }}>
        <div className="frame">
          <p className="section-kicker">Evidence behind every comparison</p>
          <h2 className="section-heading">Real observations, clear limits.</h2>
          <p className="section-intro">The interface shows the source date and resolution with the recommendation. Regional and saved data are identified as such.</p>
          <div className="source-grid">
            <article className="source-card"><Satellite size={20} /><h3>Landsat 9</h3><p>30 m vegetation, canopy moisture, bare-soil, and surface-temperature observations.</p></article>
            <article className="source-card"><Trees size={20} /><h3>SRTM terrain</h3><p>30 m elevation and slope context used to flag low-lying terrain.</p></article>
            <article className="source-card"><Map size={20} /><h3>NASA POWER</h3><p>Daily climate history summarized for seasonal heat and rainfall context.</p></article>
            <article className="source-card"><Droplets size={20} /><h3>Weather outlook</h3><p>Shown as live, saved sample, expired, or unavailable. Forecast failure does not block rotation analysis.</p></article>
          </div>
        </div>
      </section>

      <section id="rotation" className="section-space frame">
        <div className="landscape-strip">
          <div className="landscape-photo"><img src={fieldPhoto} alt="Mustard crop rows in Punjab, Pakistan, shown as an illustrative agricultural landscape" /></div>
          <div className="landscape-copy">
            <p className="section-kicker">A comparison, not a command</p>
            <h2 className="section-heading">Rotation advice should show its reasoning.</h2>
            <p className="section-intro">Each result includes a relative score, water need, benefits, risks, confidence, and whether crop rules need an expert check. It is not a yield forecast or a substitute for walking the field.</p>
            <ul className="plain-list">
              <li><ShieldCheck size={18} /> Unverified crop rules lower confidence and stay visible as warnings.</li>
              <li><Wheat size={18} /> Market demand is not assessed; confirm local seed and buyer availability.</li>
              <li><Sprout size={18} /> Environmental clusters describe data patterns, not crop health or disease.</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="frame">
        <div className="language-band">
          <div><p className="section-kicker" style={{ marginBottom: 4 }}>Designed for local use</p><strong>Farmer flow in three languages</strong></div>
          <div className="language-tags"><span>English</span><span lang="ur" dir="rtl">اردو</span><span lang="sd" dir="rtl">سنڌي</span></div>
        </div>
      </section>

      <section className="section-space frame">
        <div className="final-cta">
          <div><p className="section-kicker">No account needed</p><h2>Start with your field, then compare the options.</h2></div>
          <Button asChild size="lg"><Link href="/analyze?lang=en">Analyze my field <ArrowRight size={17} /></Link></Button>
        </div>
      </section>

      <footer className="site-footer frame">
        <p>Satellite signals support a conversation with local experts; they do not replace field inspection.</p>
        <div className="footer-row">
          <Brand />
          <div>Illustrative mustard-field photograph from Punjab, Pakistan, not an analyzed field. <a className="credit-link" href="https://commons.wikimedia.org/wiki/File:Farm_fields_of_Pakistan_in_Monsoon_season.jpg" target="_blank" rel="noreferrer">Photo: Rabia Saleem / Wikimedia Commons · CC BY-SA 4.0</a></div>
          <Link href="/expert/login" className="inline-flex min-h-11 items-center font-semibold underline-offset-4 hover:underline">Expert access</Link>
        </div>
      </footer>
    </main>
  );
}
