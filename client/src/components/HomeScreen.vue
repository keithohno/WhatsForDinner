<template>
  <div class="container">
    <Navbar current="home" />
    <div class="input-group query-input mb-3">
      <input class="form-control" v-model="filter" />
      <div class="input-group-append">
        <button class="btn btn-outline-secondary" @click="query">QUERY</button>
      </div>
    </div>
    <p>{{ server_res }}</p>
  </div>
</template>

<script>
import axios from "axios";
import Navbar from "./Navbar";

export default {
  name: "HomeScreen",
  data: () => {
    return {
      filter: "{}",
      server_res: "",
    };
  },
  methods: {
    query() {
      const path = process.env.VUE_APP_SERVER_URL + "/query";
      axios
        .post(path, { query: JSON.parse(this.filter) })
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
  },
};
</script>

<style scoped>
.query-input {
  max-width: 500px;
}
</style>
