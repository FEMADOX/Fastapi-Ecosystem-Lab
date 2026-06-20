'use client'

import { useRef, useState, type ComponentProps } from 'react'
import { cn } from '@/lib/utils'
import { Button } from './button'
import { type EyeIconHandle, EyeIcon } from './eye-icon'
import { type EyeOffIconHandle, EyeOffIcon } from './eye-off-icon'
import { Input } from './input'

interface PasswordInputProps extends ComponentProps<typeof Input> {}

const PasswordInput = ({ className, ...props }: PasswordInputProps) => {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false)
  const eyeIconRef = useRef<EyeIconHandle | EyeOffIconHandle>(null)

  return (
    <div className="relative">
      <Input
        type={isPasswordVisible ? 'text' : 'password'}
        className={cn('pr-10', className)}
        {...props}
      />
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="absolute right-2 top-1/2 -translate-y-1/2 hover:bg-transparent hover:cursor-pointer"
        aria-haspopup="false"
        onClick={() => setIsPasswordVisible((prev) => !prev)}
        onMouseEnter={() => eyeIconRef.current?.startAnimation()}
        onMouseLeave={() => eyeIconRef.current?.stopAnimation()}
      >
        <span className="relative size-4">
          <EyeIcon 
            className={`transition-opacity absolute left-0 ${isPasswordVisible ? 'opacity-0' : 'opacity-100'}`}
            ref={eyeIconRef}
            data-icon="icon" />
          <EyeOffIcon
            className={`transition-opacity absolute left-0 ${isPasswordVisible ? 'opacity-100' : 'opacity-0'}`}
            ref={eyeIconRef}
            data-icon="icon" />
        </span>
      </Button>
    </div>
  )
}

export { PasswordInput }
