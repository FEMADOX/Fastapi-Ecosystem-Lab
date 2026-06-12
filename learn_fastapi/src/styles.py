SWAGGER_GRID_STYLE = """
<style>
  .swagger-ui .wrapper {
    max-width: none;
    padding-inline: clamp(12px, 2vw, 32px);
  }

  .swagger-ui .wrapper section.block.col-12.block-desktop.col-12-desktop > div {
    align-items: start;
    display: grid;
    gap: 2rem;
    grid-template-columns: repeat(auto-fit, minmax(min(400px, 100%), 1fr));
  }

  .swagger-ui .wrapper section.block.col-12.block-desktop.col-12-desktop > div > span,
  .swagger-ui .wrapper .opblock-tag-section,
  .swagger-ui .wrapper .opblock {
    min-width: 0;
  }
</style>
"""
