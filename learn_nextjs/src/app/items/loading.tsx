import {
  Item,
  ItemContent,
  ItemDescription,
  ItemTitle
} from '@/components/ui/item'
import { Spinner } from '@/components/ui/spinner'

const Loading = () => (
  <Item>
    <Spinner className="text-muted-foreground" />
    <ItemContent>
      <ItemTitle>Loading items ...</ItemTitle>
      <ItemDescription>Please wait while we fetch the data.</ItemDescription>
    </ItemContent>
  </Item>
)
export default Loading
