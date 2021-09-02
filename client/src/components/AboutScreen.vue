<template>
  <div class="container">
    <Navbar current="about" />
    <div class="about-section">
      <div class="mb-2">Eventually, this app will have 3 primary modules:</div>
      <ul>
        <li>
          <div class="mb-2">
            Scraper -- A semi-interactive python script that populates a MongoDB
            database with recipe data pulled from online recipe catalogs. This
            module is in a mostly working state, and already has a curated
            selection of 1000 recipes and 900 ingredients in the system. It only
            pulls from allrecipes.com right now, so I might add support for
            other websites later.
          </div>
        </li>
        <li>
          <div class="mb-2">
            Backend -- A RESTful Flask API that will eventually support a
            variety of recipe/ingredient queries. At the moment, it just
            directly forwards JSON filters to the MongoDB database, and returns
            a single JSONified recipe result.
          </div>
        </li>
        <li>
          <div class="mb-2">
            Frontend -- A simple Vue-based SPA that allows users to select
            specific ingredients to use in queries. Eventually, it will include
            more options for more specific requests, as well as a more visually
            pleasing interface.
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import Navbar from "./Navbar";
export default {
  name: "AboutScreen",
  components: {
    Navbar,
  },
};
</script>

<style scoped>
.about-section {
  max-width: 750px;
}
</style>