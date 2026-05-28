import Navbar from "../components/Navbar";
import DisclaimerBanner from "../components/ui/DisclaimerBanner";

export default function LegalPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <div className="max-w-3xl mx-auto px-6 pt-28 pb-16 space-y-12">
        <h1 className="text-4xl font-bold">Legal & Disclaimers</h1>

        {/* Disclaimer Inventory */}
        <section>
          <h2 className="text-xl font-semibold mb-4 text-white/80">AI Output Disclaimers</h2>
          <div className="space-y-3">
            <DisclaimerBanner variant="score" />
            <DisclaimerBanner variant="price" />
            <DisclaimerBanner variant="document" />
            <DisclaimerBanner variant="growth" />
          </div>
        </section>

        {/* Terms of Service */}
        <section>
          <h2 className="text-xl font-semibold mb-4 text-white/80">Terms of Service</h2>
          <div className="prose prose-invert prose-sm max-w-none space-y-3 text-white/60 text-sm leading-relaxed">
            <p>
              By using PlotIQ, you agree to these terms. PlotIQ provides AI-assisted land discovery and
              verification tools for informational purposes only. The platform does not act as a real estate
              broker, legal counsel, or financial advisor.
            </p>
            <p>
              All confidence scores, price estimates, document analyses, and growth signals are generated
              by machine learning models and are subject to error. Users must independently verify all
              information before making any investment or legal decision.
            </p>
            <p>
              Sellers are responsible for the accuracy of the information they submit. PlotIQ reserves the
              right to remove listings that violate our policies or contain fraudulent information.
            </p>
            <p>
              PlotIQ may modify these terms at any time. Continued use constitutes acceptance of revised terms.
            </p>
          </div>
        </section>

        {/* Privacy Policy */}
        <section>
          <h2 className="text-xl font-semibold mb-4 text-white/80">Privacy Policy</h2>
          <div className="space-y-3 text-white/60 text-sm leading-relaxed">
            <p>
              PlotIQ collects minimal personal information required to operate the platform. We collect your
              name, email, and phone number for authentication purposes. This data is stored securely and
              is never sold to third parties.
            </p>
            <p>
              KYC data (Aadhaar, PAN) collected for seller verification is stored encrypted and is
              <strong className="text-white"> never transmitted to any AI model or language model API</strong>.
            </p>
            <p>
              Document uploads are stored in encrypted object storage. AI analysis is performed on extracted
              text only, not raw document images. Uploaded documents may be retained for up to 2 years for
              audit purposes.
            </p>
            <p>
              You may request deletion of your account and associated data by contacting us at the grievance
              address below.
            </p>
          </div>
        </section>

        {/* Grievance Contact */}
        <section>
          <h2 className="text-xl font-semibold mb-4 text-white/80">Grievance Contact</h2>
          <div className="p-4 bg-white/3 border border-white/10 rounded-xl text-sm text-white/60 space-y-2">
            <p><strong className="text-white">Grievance Officer:</strong> PlotIQ Legal Team</p>
            <p><strong className="text-white">Email:</strong> legal@plotiq.in</p>
            <p><strong className="text-white">Address:</strong> PlotIQ Systems Pvt Ltd, Hyderabad, Telangana 500032</p>
            <p className="text-xs text-white/30 pt-2">
              Grievances will be acknowledged within 48 hours and resolved within 30 days per IT Act 2000 requirements.
            </p>
          </div>
        </section>

        <p className="text-xs text-white/20 text-center pt-4">
          © 2026 PlotIQ Systems Pvt Ltd. All rights reserved. GSTIN: 36XXXXX0000X1ZX
        </p>
      </div>
    </div>
  );
}
