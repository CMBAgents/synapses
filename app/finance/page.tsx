import ChatContainer from "@/app/ui/chat-container";
import { loadFinanceData } from "@/app/utils/domain-loader";
import FloatingMenu from "@/app/ui/FloatingMenu";
import ThemeToggle from "@/app/ui/theme-toggle";
import ContextUpdater from "@/app/ui/context-updater";

export default async function FinancePage() {
  const financeData = loadFinanceData();

  return (
    <ContextUpdater domain="finance">
      <main className="min-h-screen bg-almond-beige flex flex-col">
        {/* Content */}
        <div className="mx-auto pt-4 pb-4 px-2 sm:px-4 w-full max-w-2xl lg:max-w-4xl xl:max-w-6xl text-black dark:text-white">
        {/* Header */}
        <div className="flex items-center mb-6 pt-8">
          <div className="flex items-center gap-4 flex-1">
            <div className="text-4xl">📈</div>
            <div>
              <h1 className="text-3xl font-heading">Finance & Trading</h1>
              <p className="text-gray-700 dark:text-gray-200 text-base font-inter">AI Assistant for portfolio optimization and algorithmic trading</p>
            </div>
          </div>
          <div className="flex gap-48">
            <FloatingMenu />
            <ThemeToggle />
          </div>
        </div>



        <div className="flex-1 mt-8">
          <ChatContainer
            programs={[{ 
              id: 'finance', 
              name: 'Finance & Trading', 
              description: financeData.description,
              contextFiles: [],
              docsUrl: '',
              extraSystemPrompt: `You are an AI assistant specialized in finance and trading. You have access to information about ${financeData.libraries.length} top finance libraries including: ${financeData.libraries.slice(0, 5).map(lib => lib.name).join(', ')} and more.`
            }]}
            defaultProgramId="finance"
          />
        </div>
      </div>
    </main>
    </ContextUpdater>
  );
} 