import { redirect } from 'next/navigation';

export default function Home() {
  // Redirect to landing page
  redirect('/landing');
}
