<template>
  <div class="hello">
    <input v-model="filter" />
    <button @click="query">QUERY</button>
    <p>{{ server_res }}</p>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "Home",
  data: () => {
    return {
      filter: "{}",
      server_res: ""
    };
  },
  methods: {
    query() {
      console.log("AAAA");
      const path = "http://127.0.0.1:5000/query";
      axios
        .post(path, { query: JSON.parse(this.filter) })
        .then(res => {
          console.log("success");
          this.server_res = res["data"]["res"];
        })
        .catch(error => {
          console.error(error);
        });
    }
  }
};
</script>
