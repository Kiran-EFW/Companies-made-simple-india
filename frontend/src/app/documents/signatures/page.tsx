"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
export default function SignaturesRedirect() {
  const router = useRouter();
  useEffect(() => { router.replace("/dashboard/signatures"); }, [router]);
  return null;
}
