<template>
  <div class="container">
    <Navbar current="home" />
    <div class="input-group query-input mb-3">
      <input class="form-control" v-model="filter" />
      <div class="input-group-append">
        <button class="btn btn-outline-secondary" @click="query">QUERY</button>
      </div>
    </div>
    <button class="btn btn-outline-secondary" @click="querynext">NEXT</button>
    <Recipe v-for="recipe in server_res" :recipe="recipe" :key="recipe._id" />
  </div>
</template>

<script>
import axios from "axios";
import Navbar from "./Navbar";
import Recipe from "./recipe/Recipe";

export default {
  name: "HomeScreen",
  data: () => {
    return {
      filter: "{}",
      server_res: {},
    };
  },
  methods: {
    query() {
      const path = process.env.VUE_APP_SERVER_URL + "/query";
      axios
        .post(
          path,
          { query: JSON.parse(this.filter) },
          { withCredentials: true }
        )
        .then((res) => {
          console.log("success");
          this.server_res = res["data"]["res"];
        })
        .catch((error) => {
          console.error(error);
        });
    },
    querynext() {
      const path = process.env.VUE_APP_SERVER_URL + "/querynext";
      axios
        .get(path, { withCredentials: true })
        .then((res) => {
          console.log("success");
          this.server_res = res["data"]["res"];
        })
        .catch((error) => {
          console.error(error);
        });
    },
  },
  components: {
    Navbar,
    Recipe,
  },
};
</script>

<style scoped>
.query-input {
  max-width: 500px;
}
</style>
