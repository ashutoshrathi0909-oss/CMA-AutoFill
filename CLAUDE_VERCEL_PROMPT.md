
# TASK: Fix Vercel Edge Runtime `__dirname` Error in Next.js Middleware

## Current Architecture & Completed Setup
Before debugging, please note we have successfully configured the cloud infrastructure:
1. **Railway (Backend successfully deployed):** We created a `railway.json` file mapped to the `/backend` un-nested directory and updated the start command (`uvicorn main:app --host 0.0.0.0 --port $PORT`). It is successfully running and building Nixpacks without issues. Also, `ALLOWED_ORIGINS` was set in Railway to our Vercel URL.
2. **Supabase (Auth configured):** The Vercel URL was successfully added to the Supabase Site URL and Redirect URLs (`/auth/callback`). 
3. **Vercel (Frontend deployed):** The repo root was updated to `frontend` and the build outputs successfully pass. Environment variables (`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_APP_URL`) are all successfully loaded into the Vercel project settings.

## Context & The Current Problem
We have a Next.js (App Router) project located in the `frontend` directory. We are using `@supabase/ssr` inside our `frontend/middleware.ts` file to handle authentication.

When deployed to Vercel, the application compiles successfully, but any request hitting the middleware crashes instantly with a **500 INTERNAL_SERVER_ERROR**. 

The Vercel Runtime Logs show the exact error:
`[ReferenceError: __dirname is not defined]`
`Error: MIDDLEWARE_INVOCATION_FAILED`

### Root Cause
Next.js Middleware on Vercel executes in the highly-constrained **Edge Runtime**. The Edge Runtime does not support standard Node.js global variables like `__dirname` or `__filename`. 
However, somewhere in the compilation process—likely due to an internal dependency or how `@supabase/ssr` / `next` is bundling our project—a reference to `__dirname` is being heavily injected into `.next/server/middleware.js`. When the Edge function runs on Vercel, it hits this global variable, panics, and crashes the app.

### What We Have Tried (and Failed)
1. **Downgrading Next.js:** We downgraded from `next@16.1.6` to `next@^15.1.7` (and `eslint-config-next@^15.1.7`) in `frontend/package.json` to see if the Canary bundled things differently. We also fixed a resultant TS error in Next 15 by changing `searchParams` to a Promise in `review/page.tsx` and awaiting it. **Result: The build succeeded, but the `__dirname` Edge runtime crash persisted.**
2. **Injecting Global Polyfill:** We added `// @ts-ignore \n globalThis.__dirname = globalThis.__dirname || "/";` to the top of `frontend/middleware.ts`. **Result: Failed. Vercel's bundler still tripped on `__dirname` tokens within the compiled Edge chunk.**
3. **Webpack `DefinePlugin`:** We injected a custom webpack plugin inside `next.config.ts` targeting `nextRuntime === 'edge'` that replaced `__dirname` with `JSON.stringify('/')`. **Result: Failed. Build succeeded but 500 error remains.**

## Instructions for Claude

You have access to the Vercel MCP and full repository context. Please perform the following steps to permanently resolve this Edge Runtime crash:

1. **Analyze the Deep Build Configuration:**
   Review `frontend/next.config.ts`, `frontend/tsconfig.json`, and `frontend/middleware.ts`. Determine why Edge middleware is pulling down Node modules. Are we using a Node.js-specific import by mistake? Is a specific library leaking Node code into Edge?

2. **Fix the Webpack/Next Config or Imports:**
   Locate the specific import generating the `__dirname` dependency (often related to `@supabase/ssr` or another node module) and either migrate it to an Edge-friendly version, dynamically import it out of the middleware, or use a definitive Webpack `resolve.fallback` to stub out node environments natively for Edge targets.

3. **Verify Middleware Compatibility:**
   Ensure `frontend/middleware.ts` relies strictly on Edge-compatible APIs (using `NextRequest`, `NextResponse`, and strictly Edge-safe `@supabase/ssr` implementations). 

4. **Deploy and Verify via Vercel MCP:**
   Commit the configuration changes and push to trigger a Vercel build, or use the Vercel MCP to deploy directly. 
   Monitor the Vercel deployment logs and runtime logs to confirm that the `MIDDLEWARE_INVOCATION_FAILED` (`__dirname is not defined`) error is completely eliminated and the site returns a 200 OK status on the homepage.
