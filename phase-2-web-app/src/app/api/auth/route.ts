import { SignJWT } from 'jose'
import { NextResponse } from 'next/server'

const BETTER_AUTH_SECRET = new TextEncoder().encode(
  process.env.BETTER_AUTH_SECRET || 'your-shared-secret-key-at-least-32-chars'
)

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { email, password } = body

    // Mock User Validation (In production, check DB)
    // Check for non-empty strings
    if (email && typeof email === 'string' && email.trim() !== '' && 
        password && typeof password === 'string' && password.trim() !== '') {
       // In a real "Better Auth" setup, this verifies the user against a DB.
       // Here we accept any non-empty credentials for demo purposes, 
       // but we issue a REAL signed JWT that the backend will verify.
       
       // Use email as userId to ensure persistence across logins for the same email
       const userId = email.trim()
       
       const token = await new SignJWT({ 
           sub: userId, 
           email: userId 
       })
        .setProtectedHeader({ alg: 'HS256' })
        .setIssuedAt()
        .setExpirationTime('24h')
        .sign(BETTER_AUTH_SECRET)

      return NextResponse.json({ token, user: { email, id: userId } })
    }

    return NextResponse.json(
      { error: 'Invalid credentials' },
      { status: 401 }
    )
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
