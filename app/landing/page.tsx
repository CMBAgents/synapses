import Link from 'next/link';
import styles from "../styles/background.module.css";

export default function LandingPage() {
  return (
    <main 
      className="min-h-screen bg-cover bg-center bg-no-repeat relative"
      style={{ backgroundImage: "url('/image_page2.png')" }}
    >
      {/* Dark overlay */}
      <div className="absolute inset-0 bg-black opacity-60 dark:opacity-70"></div>

      {/* Content above overlay */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 text-white page-fade-in">
        {/* Hero section */}
        <div className="text-center max-w-none mx-auto content-fade-in">
          <h1 className="text-7xl md:text-9xl font-bold mb-4 text-white font-jersey text-center uppercase">
            Synapses
          </h1>
          
          <p className="text-5xl md:text-4xl mb-12 text-white/90 font-jersey text-center italic">
            Connecting Users To Research
          </p>
          
          <p className="text-lg md:text-xl mb-16 text-white max-w-none mx-auto font-inter text-center leading-relaxed">
            <strong>Interact directly with the 100 most-starred GitHub libraries</strong> in finance and astronomy.<br/>
            Explore their capabilities through hands-on practice, and discover how they can <strong>accelerate your work</strong>.<br/>
            From portfolio optimization to cosmic microwave background analysis.
          </p>

          {/* CTA Button */}
          <div className="text-center">
            <Link 
              href="/domain-selector" 
              className="inline-block bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold py-5 px-10 rounded-full text-xl transition-all duration-300 transform hover:scale-105 hover:bg-white/30 hover:border-white/50 shadow-lg hover:shadow-xl relative overflow-hidden group font-inter nav-transition"
            >
              {/* Reflet beige */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-beige/20 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
              <span className="relative z-10">Get Started →</span>
            </Link>
          </div>
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