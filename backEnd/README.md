# Akitor backend

## Búsqueda de productos en Algolia

Akitor busca primero por todas las palabras clave extraídas del proyecto. Si no
encuentra productos, elimina progresivamente los términos de contexto
(`use`, `location`, `action` y `material`) y conserva el objeto principal para
el último intento.

El índice de Medusa debe guardar el título real del producto y permitir que el
backend lo recupere:

```js
settings: {
  [process.env.PRODUCTS_INDEX_NAME]: {
    indexSettings: {
      searchableAttributes: ['sku', 'key', 'title', 'barcode', 'brand'],
      attributesToRetrieve: ['objectID', 'sku', 'title'],
      attributesForFaceting: ['brand', 'status'],
    },
    transformer: (product) => ({
      objectID: product.id,
      key: product.key,
      sku: product.variants?.[0]?.sku,
      title: product.title,
      barcode: product.variants?.[0]?.barcode,
      brand: product.metadata?.brand?.name,
      status: product.status,
    }),
  },
}
```

Configura `ALGOLIA_APP_ID`, `ALGOLIA_SEARCH_API_KEY` y
`PRODUCTS_INDEX_NAME`. La clave debe ser una Search API Key con acceso de
lectura al índice; Akitor no necesita la Admin API Key.
