import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui'
import type { UpdateCardProps } from './types'

const UpdateCard = ({
  title,
  description,
  content,
  actionLabel,
  dialogDescription,
  icon: Icon,
  children
}: UpdateCardProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="text-muted-foreground">{content}</CardContent>
      <CardFooter>
        <Dialog>
          <DialogTrigger render={<Button className="cursor-pointer" />}>
            <Icon data-icon="inline-start" />
            {actionLabel}
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{title}</DialogTitle>
              <DialogDescription>{dialogDescription}</DialogDescription>
            </DialogHeader>

            {children}
          </DialogContent>
        </Dialog>
      </CardFooter>
    </Card>
  )
}

export default UpdateCard
