"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
export default function AccountingRedirect() {
  const router = useRouter();
  useEffect(() => { router.replace("/dashboard/accounting"); }, [router]);
  return null;
}
