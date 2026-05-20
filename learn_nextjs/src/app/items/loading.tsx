import {
  Item,
  ItemContent,
  ItemDescription,
  ItemTitle,
  Spinner
} from '@/components/ui'

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
