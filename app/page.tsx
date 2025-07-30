import ChatContainer from "@/app/ui/chat-container";
import { loadConfig, getDefaultProgram } from "@/app/utils/config";

export default async function Home() {
  // Load configuration
  const config = loadConfig();
  const defaultProgram = getDefaultProgram();

  return (
    <main className="min-h-screen bg-white dark:bg-gray-900">
      <div className="mx-auto my-4 sm:my-8 px-2 sm:px-4 w-full max-w-2xl lg:max-w-4xl xl:max-w-6xl">
        <ChatContainer
          programs={config.programs}
          defaultProgramId={defaultProgram.id}
        />
      </div>
    </main>
  );
}
