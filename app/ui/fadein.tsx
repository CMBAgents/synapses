"use client";

import { useEffect, useState, ReactNode } from "react";

type FadeInProps = {
  children: ReactNode;
  duration?: number; // ms
};

export default function FadeIn({ children, duration = 1000 }: FadeInProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setVisible(true);
  }, []);

  return (
    <div
      style={{
        opacity: visible ? 1 : 0,
        transition: `opacity ${duration}ms ease-in-out`,
      }}
    >
      {children}
    </div>
  );
}
