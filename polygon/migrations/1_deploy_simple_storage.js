const vc4med= artifacts.require("vc4med");
const Example = artifacts.require("example")

module.exports = function (deployer) {
  deployer.deploy(vc4med);
  deployer.deploy(Example)
};
