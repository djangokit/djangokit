/* Users Page */

export default function Page({ data }: { data: any }) {
  return <h1>Users ({data.users.length})</h1>;
}
