import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

export function setToken(token) {
  axios.defaults.headers.common["Authorization"] = token ? `Bearer ${token}` : "";
}

export async function login(username, password) {
  const params = new URLSearchParams();
  params.append("username", username);
  params.append("password", password);
    const r = await axios.post(`${API_BASE}/token`, params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });
  return r.data;
}

export async function listOrgs() {
  return (await axios.get(`${API_BASE}/orgs`)).data;
}

export async function createOrg(org_id, org_name) {
  return (await axios.post(`${API_BASE}/admin/orgs`, { org_id, org_name })).data;
}

export async function createUser(org_id, username, password, role) {
  return (await axios.post(`${API_BASE}/orgs/${encodeURIComponent(org_id)}/users`, { username, password, role })).data;
}

export async function listUsers(org_id) {
  return (await axios.get(`${API_BASE}/orgs/${encodeURIComponent(org_id)}/users`)).data;
}

export async function deleteUser(org_id, username) {
  return (await axios.delete(`${API_BASE}/orgs/${encodeURIComponent(org_id)}/users/${encodeURIComponent(username)}`)).data;
}