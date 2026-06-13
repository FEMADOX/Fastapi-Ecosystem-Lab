"use client"

import { cn } from "@/lib/utils"

// Keep native form semantics behind the shared UI API for server actions and accessibility.
function Form({ className, ...props }: React.ComponentProps<"form">) {
  return (
    <form
      data-slot="form"
      className={cn("flex flex-col gap-4", className)}
      {...props}
    />
  )
}

export { Form }
