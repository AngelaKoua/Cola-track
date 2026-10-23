"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/Card"
import { Lock, Mail, ArrowRight } from "lucide-react"
import { useAuth } from "@/context/AuthContext"

export default function LoginPage() {
  const router = useRouter()
  const { login } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      // Dynamic import to avoid SSR issues if api.ts uses browser-only features, though in this case it's fine.
      // Better to import at top, but for replacing logic block:
      const { authApi } = await import("@/lib/api")
      const data = await authApi.login(username, password)

      // Use AuthContext login which handles storage and state update
      login(data.username, data.role, data.access_token, data.user_id)

      // Router push is handled inside login() but redundancy is fine or we can rely on context
    } catch (err: any) {
      console.error(err)
      setError("Identifiants incorrects. Veuillez réessayer.")
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden">
      {/* Background Decoration */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-primary/5 blur-[100px]" />
        <div className="absolute top-[40%] right-[0%] w-[40%] h-[40%] rounded-full bg-accent-blue/5 blur-[100px]" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="z-10 w-full max-w-md px-4"
      >
        <div className="text-center flex flex-col items-center justify-center">
          <div className="relative w-80 h-50">
            <Image
              src="/Ctrack_login.png"
              alt="Logo"
              fill
              className="object-contain"
              priority
            />
          </div>
          {/*<p className="text-lg text-gray-600 font-medium">See. Predict. Perform.</p>*/}
        </div>

        <Card className="border-gray-200 shadow-xl bg-white/80 backdrop-blur-sm">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Connexion</CardTitle>
            <CardDescription className="text-center">
              Entrez vos identifiants pour accéder à la plateforme
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-4">
                {error && (
                  <div className="p-3 bg-red-50 text-red-500 text-sm rounded-md border border-red-100">
                    {error}
                  </div>
                )}
                <div className="space-y-2">
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      type="text"
                      placeholder="Nom d'utilisateur"
                      className="pl-9"
                      required
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      type="password"
                      placeholder="Mot de passe"
                      className="pl-9"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </div>
                </div>
              </div>
              <Button
                type="submit"
                className="w-full bg-primary hover:bg-primary/90 text-white"
                disabled={isLoading}
              >
                {isLoading ? (
                  "Connexion en cours..."
                ) : (
                  <>
                    Se connecter <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex flex-col space-y-2">
            <div className="text-sm text-center text-gray-500">
              <a href="#" className="hover:text-primary underline underline-offset-4">
                Mot de passe oublié ?
              </a>
            </div>
            <div className="relative w-full">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-gray-200" />
              </div>
            </div>
          </CardFooter>
        </Card>

        <p className="mt-8 text-center text-xs text-gray-400">
          © 2026 Coca-Cola Industrial Solutions. All rights reserved.
        </p>
      </motion.div>
    </div>
  )
}
