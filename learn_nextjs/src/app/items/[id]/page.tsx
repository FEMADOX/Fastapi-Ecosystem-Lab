export const Item = ({ params }: { params: { id: string } }) => {
  return (
    <>
      <h1>Item {params.id}</h1>
      <p>Here should be the details of the item with id {params.id}</p>
    </>
  )
}
