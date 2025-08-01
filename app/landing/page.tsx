import Link from 'next/link';
import styles from "../styles/background.module.css";

export default function LandingPage() {
  return (
    <main 
      className="min-h-screen bg-cover bg-center bg-no-repeat relative"
      style={{ backgroundImage: "url('/image_page2.png')" }}
    >
      {/* Dark overlay */}
      <div className="absolute inset-0 bg-black opacity-30 dark:opacity-50"></div>

      {/* Content above overlay */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 text-white page-fade-in">
        {/* Hero section */}
        <div className="text-center max-w-4xl mx-auto content-fade-in">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-white font-jersey">
            CMBAgent Info
          </h1>
          
          <p className="text-xl md:text-2xl mb-8 text-white leading-relaxed font-inter">
            Your <strong>AI-powered assistant</strong> for cosmology and finance tools
          </p>
          
          <p className="text-lg md:text-xl mb-12 text-white max-w-3xl mx-auto font-inter">
            Access the <strong>100 most-starred GitHub libraries</strong> in finance and astronomy. 
            From portfolio optimization to cosmic microwave background analysis, 
            get instant insights and code execution.
          </p>

          {/* Feature highlights */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
              <div className="text-3xl mb-3">🚀</div>
              <h3 className="text-lg font-semibold mb-2 text-white font-inter">Instant Access</h3>
              <p className="text-sm text-white font-inter">No setup required, just smart execution</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
              <div className="text-3xl mb-3">💡</div>
              <h3 className="text-lg font-semibold mb-2 text-white font-inter">AI-Powered</h3>
              <p className="text-sm text-white font-inter">Fluent in the language of top libraries</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
              <div className="text-3xl mb-3">🔬</div>
              <h3 className="text-lg font-semibold mb-2 text-white font-inter">Multi-Domain</h3>
              <p className="text-sm text-white font-inter">Finance to cosmology expertise</p>
            </div>
          </div>

          {/* CTA Button */}
          <Link 
            href="/domain-selector" 
            className="inline-block bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-4 px-8 rounded-full text-lg transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl relative overflow-hidden group font-inter nav-transition"
          >
            {/* Reflet beige */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-beige/20 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
            <span className="relative z-10">Get Started →</span>
          </Link>
        </div>

        {/* Footer */}
        <div className="absolute bottom-8 text-center text-white">
          <p className="text-sm font-inter">
            Powered by Next.js • Built for researchers and developers
          </p>
        </div>
      </div>

    </main>
  );
} 