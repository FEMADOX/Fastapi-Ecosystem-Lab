import { Spinner } from '@/components/ui/spinner'

const Loading = () => (
  <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3">
    <Spinner className="text-primary size-8" />
    <p className="text-muted-foreground text-sm">Loading...</p>
  </div>
)

export default Loading
