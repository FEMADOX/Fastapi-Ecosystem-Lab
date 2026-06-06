import Image from 'next/image'
import { NO_IMAGE_AVAILABLE_URL } from '@/common/const'

const IMAGE_EXTENSION_PATTERN = /\.(avif|gif|jpe?g|png|svg|webp)$/i

const getSafeImageSrc = (src?: string | null) => {
  if (!src) return NO_IMAGE_AVAILABLE_URL
  if (src.startsWith('/')) return src

  try {
    const url = new URL(src)
    return IMAGE_EXTENSION_PATTERN.test(url.pathname)
      ? url.toString()
      : NO_IMAGE_AVAILABLE_URL
  } catch {
    return NO_IMAGE_AVAILABLE_URL
  }
}

interface ProductImageProps {
  src?: string | null
  alt: string
  className?: string
  width?: number
  height?: number
  loading?: 'eager' | 'lazy'
}

export const ProductImage = ({
  src,
  alt,
  className,
  width = 500,
  height = 500,
  loading = 'eager'
}: ProductImageProps) => {
  const safeSrc = getSafeImageSrc(src)

  if (safeSrc.startsWith('/')) {
    return (
      <Image
        src={safeSrc}
        alt={alt}
        className={className}
        width={width}
        height={height}
        loading={loading}
      />
    )
  }

  return (
    <img
      src={safeSrc}
      alt={alt}
      className={className}
      width={width}
      height={height}
      loading={loading}
      referrerPolicy="no-referrer"
    />
  )
}
