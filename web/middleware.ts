import { NextResponse, type NextRequest } from "next/server";

/** Protège /admin par un identifiant et un mot de passe (variables ADMIN_USER et ADMIN_PASSWORD). */
export function middleware(req: NextRequest) {
  const user = process.env.ADMIN_USER;
  const pass = process.env.ADMIN_PASSWORD;
  if (!user || !pass) return new NextResponse("Back-office désactivé : définissez ADMIN_USER et ADMIN_PASSWORD.", { status: 503 });
  const header = req.headers.get("authorization") || "";
  const [scheme, encoded] = header.split(" ");
  if (scheme === "Basic" && encoded) {
    const [u, ...rest] = atob(encoded).split(":");
    if (u === user && rest.join(":") === pass) return NextResponse.next();
  }
  return new NextResponse("Authentification requise", { status: 401, headers: { "WWW-Authenticate": 'Basic realm="Wabo admin"' } });
}

export const config = { matcher: ["/admin/:path*"] };
