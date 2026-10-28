/* Recette de MangoTrack : verifie le contrat de l'API point par point.
   Logique pure (sans DOM) : utilisable dans le navigateur et dans Node. */
(function () {
  const BASE = (typeof window !== "undefined") ? "" : (process.env.BASE || "http://127.0.0.1:8000");

  async function appel(methode, chemin, corps) {
    const opts = { method: methode, headers: { Accept: "application/json" } };
    if (corps !== undefined) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(corps);
    }
    try {
      const r = await fetch(BASE + chemin, opts);
      const texte = await r.text();
      let json = null;
      try { json = texte ? JSON.parse(texte) : null; } catch (e) { /* pas du JSON */ }
      return { status: r.status, json, texte, entetes: r.headers };
    } catch (e) {
      return { status: 0, json: null, texte: String(e), entetes: new Headers() };
    }
  }

  function attendu(res, code) {
    if (res.status === code) return null;
    if (res.status === 0) return "Failed to fetch : le serveur est arrete ou l'adresse est mauvaise.";
    if (res.status === 501) return "501 : le TODO de cette route n'est pas encore ecrit.";
    if (res.status === 500) return "500 : erreur dans ton code. Lis la premiere ligne de l'erreur dans le terminal.";
    return "attendu " + code + ", recu " + res.status + ".";
  }

  const TESTS = [];
  function t(id, niveau, titre, carte, indice, run) { TESTS.push({ id, niveau, titre, carte, indice, run }); }
  const suf = Date.now().toString(36);
  const ABSENT = 999999;

  // ------------------------------ SOCLE (9) ------------------------------
  t("S1", "Socle", "POST /api/producteurs valide repond 201", "A1",
    "Que doit savoir le client quand la creation a reussi ?", async (c) => {
      c.nom1 = "Awa-" + suf;
      const r = await appel("POST", "/api/producteurs", { nom: c.nom1, village: "Orodara" });
      const e = attendu(r, 201); if (e) return e;
      if (!r.json || !r.json.id) return "la reponse doit contenir l'objet cree, avec son id.";
      c.id1 = r.json.id; return null;
    });
  t("S2", "Socle", "GET /api/producteurs/{id} repond 200 avec le producteur", "A2",
    "Quelle forme prend une ressource quand on la lit ?", async (c) => {
      if (!c.id1) return "depend de S1 : aucun producteur cree.";
      const r = await appel("GET", "/api/producteurs/" + c.id1);
      const e = attendu(r, 200); if (e) return e;
      if (!r.json || r.json.nom !== c.nom1) return "le JSON renvoye ne contient pas le bon nom.";
      return null;
    });
  t("S3", "Socle", "GET d'un producteur inexistant repond 404", "A3",
    "Que dit l'adresse quand rien ne correspond ?", async () =>
      attendu(await appel("GET", "/api/producteurs/" + ABSENT), 404));
  t("S4", "Socle", "POST sans nom repond 422", "A4",
    "Une donnee invalide est refusee avant ou apres l'ecriture ?", async () =>
      attendu(await appel("POST", "/api/producteurs", {}), 422));
  t("S5", "Socle", "POST avec un nom vide repond 422", "A4",
    "Une donnee invalide est refusee avant ou apres l'ecriture ?", async () =>
      attendu(await appel("POST", "/api/producteurs", { nom: "" }), 422));
  t("S6", "Socle", "GET /api/producteurs renvoie la liste avec le producteur cree", "A2",
    "Quelle forme prend une ressource quand on la lit ?", async (c) => {
      if (!c.id1) return "depend de S1 : aucun producteur cree.";
      const r = await appel("GET", "/api/producteurs");
      const e = attendu(r, 200); if (e) return e;
      if (!Array.isArray(r.json)) return "la liste doit etre un tableau JSON.";
      if (!r.json.some((p) => p.id === c.id1)) return "le producteur cree n'apparait pas dans la liste.";
      return null;
    });
  t("S7", "Socle", "PUT /api/producteurs/{id} modifie et repond 200", "A5",
    "Quel code pour une modification ?", async (c) => {
      if (!c.id1) return "depend de S1 : aucun producteur cree.";
      const nouveau = "Awa Traore-" + suf;
      const r = await appel("PUT", "/api/producteurs/" + c.id1, { nom: nouveau, village: "Orodara" });
      const e = attendu(r, 200); if (e) return e;
      if (!r.json || r.json.nom !== nouveau) return "le producteur renvoye n'a pas le nouveau nom.";
      c.nom1 = nouveau; return null;
    });
  t("S8", "Socle", "Un doublon de nom est refuse (422), pas une erreur 500", "A6",
    "Que sait la validation de la contrainte UNIQUE du modele ?", async (c) => {
      if (!c.id1) return "depend de S1 : aucun producteur cree.";
      const r = await appel("POST", "/api/producteurs", { nom: c.nom1, village: "Autre" });
      if (r.status === 500) return "500 : le doublon n'est pas gere (contrainte unique perdue ? laisse le ModelSerializer lire le modele).";
      return attendu(r, 422);
    });
  t("S9", "Socle", "DELETE repond 204, puis le GET repond 404", "A5",
    "Quel code pour une suppression ?", async () => {
      const cree = await appel("POST", "/api/producteurs", { nom: "Supprime-" + suf, village: "X" });
      if (cree.status !== 201) return "impossible de preparer le test : termine d'abord S1.";
      const id = cree.json.id;
      const e1 = attendu(await appel("DELETE", "/api/producteurs/" + id), 204); if (e1) return e1;
      const e2 = attendu(await appel("GET", "/api/producteurs/" + id), 404);
      return e2 ? "apres la suppression : " + e2 : null;
    });

  // ------------------------------ CIBLE (11) -----------------------------
  async function livrer(c, corps) { return appel("POST", "/api/livraisons", Object.assign({ producteur: c.pid, variete: "Kent" }, corps)); }
  async function stock(c) {
    const r = await appel("GET", "/api/producteurs/" + c.pid + "/stock");
    return { r, valeur: r.json ? Number(r.json.stock_kg) : NaN };
  }
  const sansC0 = "depend de C0 : le producteur de test n'a pas pu etre cree.";

  t("C0", "Cible", "Preparation : un producteur est cree pour les tests de livraison", "—",
    "Cette etape a besoin de POST /api/producteurs.", async (c) => {
      const r = await appel("POST", "/api/producteurs", { nom: "Cible-" + suf, village: "Banfora" });
      if (r.status !== 201) return "Termine d'abord le niveau Socle (" + (attendu(r, 201)) + ")";
      c.pid = r.json.id; return null;
    });
  t("C1", "Cible", "POST /api/livraisons (entree de 40 kg) repond 201", "B1",
    "Une livraison appartient a qui ? Ou est la cle ?", async (c) => {
      if (!c.pid) return sansC0;
      const r = await livrer(c, { poids_kg: 40, sens: "entree" });
      const e = attendu(r, 201); if (e) return e;
      if (!r.json || !r.json.id) return "la reponse doit contenir la livraison creee.";
      return null;
    });
  t("C2", "Cible", "Un poids negatif est refuse (422)", "B2",
    "Quelles valeurs sont interdites pour un poids ?", async (c) =>
      c.pid ? attendu(await livrer(c, { poids_kg: -5, sens: "entree" }), 422) : sansC0);
  t("C3", "Cible", "Un poids nul est refuse (422)", "B2",
    "Quelles valeurs sont interdites pour un poids ?", async (c) =>
      c.pid ? attendu(await livrer(c, { poids_kg: 0, sens: "entree" }), 422) : sansC0);
  t("C4", "Cible", "Un producteur inexistant dans le corps est refuse (422)", "B3",
    "Un producteur inconnu dans le corps est-il une adresse introuvable ?", async () => {
      const r = await appel("POST", "/api/livraisons", { producteur: ABSENT, variete: "Kent", poids_kg: 10, sens: "entree" });
      if (r.status === 404) return "404 : un producteur inconnu dans le CORPS est une donnee invalide, donc 422.";
      return attendu(r, 422);
    });
  t("C5", "Cible", "Un sens inconnu est refuse (422)", "B2",
    "Quelles valeurs sont interdites pour un sens ?", async (c) =>
      c.pid ? attendu(await livrer(c, { poids_kg: 10, sens: "vol" }), 422) : sansC0);
  t("C6", "Cible", "Une sortie superieure au stock repond 409", "B4",
    "Une sortie de 50 kg avec 40 kg en stock : valide ?", async (c) => {
      if (!c.pid) return sansC0;
      const r = await livrer(c, { poids_kg: 50, sens: "sortie" });
      if (r.status === 201) return "201 : la sortie de 50 kg a ete acceptee alors qu'il n'y a que 40 kg.";
      return attendu(r, 409);
    });
  t("C7", "Cible", "Apres ce refus, le stock vaut toujours 40 kg", "B5",
    "Un refus ecrit-il quelque chose ?", async (c) => {
      if (!c.pid) return sansC0;
      const { r, valeur } = await stock(c);
      const e = attendu(r, 200); if (e) return e;
      return valeur === 40 ? null : "stock_kg vaut " + r.json.stock_kg + " au lieu de 40.";
    });
  t("C8", "Cible", "Une sortie de 15 kg est acceptee (201) et le stock passe a 25 kg", "B5",
    "Comment calcule-t-on le stock ?", async (c) => {
      if (!c.pid) return sansC0;
      const e = attendu(await livrer(c, { poids_kg: 15, sens: "sortie" }), 201); if (e) return e;
      const { valeur, r } = await stock(c);
      return valeur === 25 ? null : "stock_kg vaut " + (r.json && r.json.stock_kg) + " au lieu de 25.";
    });
  t("C9", "Cible", "Une sortie egale au stock est acceptee : le stock tombe a 0", "B4",
    "Une sortie de 50 kg avec 40 kg en stock : valide ? Et 40 kg ?", async (c) => {
      if (!c.pid) return sansC0;
      const e = attendu(await livrer(c, { poids_kg: 25, sens: "sortie" }), 201); if (e) return e;
      const { valeur, r } = await stock(c);
      return valeur === 0 ? null : "stock_kg vaut " + (r.json && r.json.stock_kg) + " au lieu de 0.";
    });
  t("C10", "Cible", "Supprimer un producteur qui a des livraisons repond 409", "B6",
    "Que protege la cle etrangere quand on supprime un producteur ?", async (c) => {
      if (!c.pid) return sansC0;
      const r = await appel("DELETE", "/api/producteurs/" + c.pid);
      if (r.status === 204) return "204 : le producteur a ete supprime alors qu'il avait des livraisons.";
      return attendu(r, 409);
    });

  // ------------------------------ DEFI (5) -------------------------------
  async function preparerDefi(c) {
    if (c.defi !== undefined) return c.defi;
    c.defi = "Termine d'abord la Cible : les defis ont besoin des livraisons.";
    const p1 = await appel("POST", "/api/producteurs", { nom: "Defi1-" + suf, village: "X" });
    const p2 = await appel("POST", "/api/producteurs", { nom: "Defi2-" + suf, village: "Y" });
    if (p1.status !== 201 || p2.status !== 201) return c.defi;
    c.d1 = p1.json.id; c.d2 = p2.json.id;
    for (const [p, n] of [[c.d1, 3], [c.d2, 1]]) {
      for (let i = 0; i < n; i++) {
        const r = await appel("POST", "/api/livraisons", { producteur: p, variete: "Kent", poids_kg: 10, sens: "entree" });
        if (r.status !== 201) return c.defi;
      }
    }
    c.defi = null; return null;
  }
  t("D1", "Defi", "Pagination : ?page=1&per_page=2 renvoie 2 lignes, la page 2 en renvoie d'autres", "C1",
    "Combien de lignes peut-on envoyer d'un coup sur une connexion lente ?", async (c) => {
      const p = await preparerDefi(c); if (p) return p;
      const a = await appel("GET", "/api/livraisons?page=1&per_page=2");
      const e = attendu(a, 200); if (e) return e;
      if (!Array.isArray(a.json) || a.json.length !== 2) return "la page 1 devrait contenir exactement 2 livraisons.";
      const b = await appel("GET", "/api/livraisons?page=2&per_page=2");
      if (!Array.isArray(b.json) || b.json.length === 0) return "la page 2 est vide.";
      const ids = a.json.map((x) => x.id);
      if (b.json.some((x) => ids.includes(x.id))) return "la page 2 repete des lignes de la page 1.";
      return null;
    });
  t("D2", "Defi", "Pagination : l'en-tete X-Total-Count donne le total", "C1",
    "Comment le client sait-il combien de pages il reste ?", async (c) => {
      const p = await preparerDefi(c); if (p) return p;
      const r = await appel("GET", "/api/livraisons?page=1&per_page=2");
      const total = Number(r.entetes.get("X-Total-Count"));
      if (!Number.isFinite(total) || r.entetes.get("X-Total-Count") === null) return "en-tete X-Total-Count absent.";
      return total >= 4 ? null : "X-Total-Count vaut " + total + " : attendu au moins 4.";
    });
  t("D3", "Defi", "Filtre : ?producteur_id=... ne renvoie que ses livraisons", "C2",
    "Un filtre est-il une nouvelle adresse ou un parametre ?", async (c) => {
      const p = await preparerDefi(c); if (p) return p;
      const r = await appel("GET", "/api/livraisons?producteur_id=" + c.d1);
      const e = attendu(r, 200); if (e) return e;
      if (!Array.isArray(r.json) || r.json.length !== 3) return "attendu 3 livraisons pour ce producteur, recu " + (Array.isArray(r.json) ? r.json.length : "autre chose") + ".";
      return r.json.every((x) => x.producteur === c.d1) ? null : "des livraisons d'un autre producteur sont renvoyees.";
    });
  function formeErreur(r) {
    return r.json && typeof r.json.message === "string" && Object.prototype.hasOwnProperty.call(r.json, "errors");
  }
  t("D4", "Defi", "Erreurs structurees : le 404 et le 422 ont la forme {message, errors}", "C3",
    "Qui lira vos erreurs ? Combien de formes faut-il ?", async () => {
      const a = await appel("GET", "/api/producteurs/" + ABSENT);
      if (a.status !== 404) return attendu(a, 404);
      if (!formeErreur(a)) return "le 404 doit avoir la forme {\"message\": ..., \"errors\": ...}.";
      const b = await appel("POST", "/api/producteurs", {});
      if (b.status !== 422) return attendu(b, 422);
      return formeErreur(b) ? null : "le 422 doit avoir la forme {\"message\": ..., \"errors\": ...}.";
    });
  t("D5", "Defi", "Erreurs structurees : le 409 a la forme {message, errors}", "C3",
    "Qui lira vos erreurs ? Combien de formes faut-il ?", async (c) => {
      const p = await preparerDefi(c); if (p) return p;
      const a = await appel("POST", "/api/livraisons", { producteur: c.d2, variete: "Kent", poids_kg: 1000000, sens: "sortie" });
      if (a.status !== 409) return attendu(a, 409);
      if (!formeErreur(a)) return "le 409 (stock) doit avoir la forme {\"message\": ..., \"errors\": ...}.";
      const b = await appel("DELETE", "/api/producteurs/" + c.d2);
      if (b.status !== 409) return attendu(b, 409);
      return formeErreur(b) ? null : "le 409 (suppression) doit avoir la forme {\"message\": ..., \"errors\": ...}.";
    });

  async function lancer(surResultat) {
    const c = {}; const bilan = [];
    for (const test of TESTS) {
      let erreur;
      try { erreur = await test.run(c); } catch (e) { erreur = "erreur de la recette : " + e; }
      const res = { id: test.id, niveau: test.niveau, titre: test.titre, carte: test.carte, indice: test.indice, ok: !erreur, detail: erreur };
      bilan.push(res); if (surResultat) surResultat(res);
    }
    return bilan;
  }

  const API = { TESTS, lancer, appel };
  if (typeof window !== "undefined") window.RECETTE = API;
  if (typeof module !== "undefined") module.exports = API;
})();
