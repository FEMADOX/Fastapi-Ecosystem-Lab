import { Spinner } from '@/components/ui/spinner'

const Loading = () => (
  <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3">
    <Spinner className="size-8 text-primary" />
    <p className="text-sm text-muted-foreground">Loading...</p>
  </div>
)

export default Loading
