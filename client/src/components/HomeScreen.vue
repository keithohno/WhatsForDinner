<template>
  <div class="container my-box">
    <div class="row">
      <Navbar current="home" />
    </div>
    <div class="row my-querybox mb-4 pt-2 pb-3">
      <QueryOptions @query="query" />
    </div>
    <button class="btn btn-outline-secondary" @click="querynext">NEXT</button>
    <Recipe v-for="recipe in server_res" :recipe="recipe" :key="recipe._id" />
  </div>
</template>

<script>
import axios from "axios";
import Navbar from "./Navbar";
import Recipe from "./recipe/Recipe";
import QueryOptions from "./QueryOptions";

export default {
  name: "HomeScreen",
  data: () => {
    return {
      server_res: {},
    };
  },
  computed: {
    ingredients() {
      return this.$store.state.ingredients;
    },
  },
  methods: {
    query() {
      let filter_ingredients = this.ingredients.filter((x) => x != "");
      let filter = {
        query: {
          ingredients: { $all: filter_ingredients },
        },
      };
      const path = process.env.VUE_APP_SERVER_URL + "/query";
      axios
        .post(path, filter, { withCredentials: true })
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
    QueryOptions,
  },
};
</script>

<style scoped>
.my-box {
  max-width: 600px;
}
.my-querybox {
  padding: 4px;
  border: 3px solid #e9f5ff;
}
</style>